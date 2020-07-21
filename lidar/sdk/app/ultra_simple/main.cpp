/*
*  RPLIDAR
*  Ultra Simple Data Grabber Demo App
*
*  Copyright (c) 2009 - 2014 RoboPeak Team
*  http://www.robopeak.com
*  Copyright (c) 2014 - 2019 Shanghai Slamtec Co., Ltd.
*  http://www.slamtec.com
*
*/
/*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
*/
#define TWO_PIE 6.28318530718
#define INCH_PER_MM 1/25.4

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <vector>
#include <algorithm>
#include "math.h"


#include "rplidar.h" //RPLIDAR standard sdk, all-in-one header

#include "opencv2/opencv.hpp"

#ifndef _countof
#define _countof(_Array) (int)(sizeof(_Array) / sizeof(_Array[0]))
#endif

#ifndef _to_radians
#define _to_radians(deg) (deg * 3.14159 / 180)
#define _constrain_angle(_radians) ((_radians % TWO_PIE + TWO_PIE) % TWO_PIE)
#endif

#ifdef _WIN32
#include <Windows.h>
#define delay(x)   ::Sleep(x)
#else
#include <unistd.h>
static inline void delay(_word_size_t ms) {
	while (ms >= 1000) {
		usleep(1000 * 1000);
		ms -= 1000;
	};
	if (ms != 0)
		usleep(ms * 1000);
}
#endif


using namespace rp::standalone::rplidar;

struct LidarData {
	//(azimuth, distance, rel_angle, quality)
	double azimuth;
	double distance;
	double rel_angle;
	int quality;
};

bool checkRPLIDARHealth(RPlidarDriver * drv)
{
	//std::cout << "in check rplidar health function\n";
	u_result     op_result;
	rplidar_response_device_health_t healthinfo;

	//std::cout << "abt to get health in rplidar health func\n";
	op_result = drv->getHealth(healthinfo);

	//std::cout << "op_result from drv->getHealth()" << op_result << "\n";
	if (IS_OK(op_result)) { // the macro IS_OK is the preperred way to judge whether the operation is succeed.
		printf("RPLidar health status : %d\n", healthinfo.status);
		if (healthinfo.status == RPLIDAR_STATUS_ERROR) {
			fprintf(stderr, "Error, rplidar internal error detected. Please reboot the device to retry.\n");
			// enable the following code if you want rplidar to be reboot by software
			// drv->reset();
			return false;
		}
		else {
			return true;
		}

	}
	else {
		fprintf(stderr, "Error, cannot retrieve the lidar health code: %x\n", op_result);
		return false;
	}
}

#include <signal.h>
bool ctrl_c_pressed;
void ctrlc(int)
{
	ctrl_c_pressed = true;
}

int main(int argc, const char* argv[]) {
	const char* opt_com_path = NULL;
	_u32         baudrateArray[2] = { 115200, 256000 };
	_u32         opt_com_baudrate = 0;
	u_result     op_result;

	bool useArgcBaudrate = false;

	// ANGLE OF THE LIDAR FROM HORIZONTAL, in radians
	double lidarAngle = 0;
	// minimum quality of lidar data
	const int MIN_QUALITY = 10;
	// distance resolution of the hough line transform in mm
	// mm per pixel (of opencv image)
	const int MM_RESOLUTION = 20;
	// angle resolution of the hough line transform in deg
	const int ANGLE_RESOLUTION = 1;
	// radius in mm to consider for line detection
	const int RADIUS = 7000;
	// WIDTH OF THE LINE WE ARE LOOKING FOR, in PIXELS
	const int LINE_LENGTH = 1220 / MM_RESOLUTION;
	// allowable error in the length of the line for it to still be counted
	const int ALLOWABLE_LEN_ERROR = (int) (254 / MM_RESOLUTION);
	// Angular range the lidar should look in its map for
	const int ANGULAR_RANGE = 60;
	// number of columns in the matrix
	int numCols = RADIUS * 2 / MM_RESOLUTION + 2;
	int numRows = RADIUS / MM_RESOLUTION + 1;
	// column index that is 0mm to MM_RESOLUTION mm
	int centerIndex = numCols / 2;
	// store the matrix to pass into hough transform function
	cv::Mat view(numRows, numCols, CV_8U, cv::Scalar(0));
	cv::Mat defaultImage(numRows, numCols, CV_8UC1, cv::Scalar(100));
	// store the lines found through hough transform
	std::vector<cv::Vec4i> linesResult;

	printf("Starting lidar!\n"
		"Version: " RPLIDAR_SDK_VERSION "\n");

	// read angle from command line...
	if (argc > 1)
	{
		lidarAngle = strtod(argv[1], NULL);
		lidarAngle *= TWO_PIE / 360;
	}
	// read serial port from command line... e.g. "com8"
	if (argc > 2) {
		opt_com_path = argv[2];
	}
	// read baud rate from command line if specified
	if (argc > 3) {
		opt_com_baudrate = strtoul(argv[3], NULL, 10);
		useArgcBaudrate = true;
	}

	if (!opt_com_path) {
#ifdef _WIN32
		// use default com port
		opt_com_path = "\\\\.\\com8";
#elif __APPLE__
		opt_com_path = "/dev/tty.SLAB_USBtoUART";
#else
		opt_com_path = "/dev/ttyUSB0";
#endif
	}

	// create the driver instance
	RPlidarDriver* drv = RPlidarDriver::CreateDriver(DRIVER_TYPE_SERIALPORT);
	if (!drv) {
		fprintf(stderr, "insufficent memory, exit\n");
		exit(-2);
	}

	rplidar_response_device_info_t devinfo;
	bool connectSuccess = false;
	// make connection...
	if (useArgcBaudrate)
	{
		if (!drv)
			drv = RPlidarDriver::CreateDriver(DRIVER_TYPE_SERIALPORT);
		if (IS_OK(drv->connect(opt_com_path, opt_com_baudrate)))
		{
			op_result = drv->getDeviceInfo(devinfo);

			if (IS_OK(op_result))
			{
				connectSuccess = true;
			}
			else
			{
				delete drv;
				drv = NULL;
			}
		}
	}
	else
	{
		size_t baudRateArraySize = (sizeof(baudrateArray)) / (sizeof(baudrateArray[0]));
		for (size_t i = 0; i < baudRateArraySize; ++i)
		{
			std::cout << "insdie for loop on line 155, " << baudrateArray[i] << "\n";
			if (!drv) {
				std::cout << "in !drv on line 157\n";
				drv = RPlidarDriver::CreateDriver(DRIVER_TYPE_SERIALPORT);
			}
			if (IS_OK(drv->connect(opt_com_path, baudrateArray[i])))
			{
				op_result = drv->getDeviceInfo(devinfo);

				if (IS_OK(op_result))
				{
					connectSuccess = true;
					break;
				}
				else
				{
					delete drv;
					drv = NULL;
				}
			}
		}
	}
	if (!connectSuccess) {

		fprintf(stderr, "Error, cannot bind to the specified serial port %s.\n"
			, opt_com_path);
		goto on_finished;
	}

	// print out the device serial number, firmware and hardware version number..
	printf("RPLIDAR S/N: ");
	for (int pos = 0; pos < 16; ++pos) {
		printf("%02X", devinfo.serialnum[pos]);
	}

	printf("\n"
		"Firmware Ver: %d.%02d\n"
		"Hardware Rev: %d\n"
		, devinfo.firmware_version >> 8
		, devinfo.firmware_version & 0xFF
		, (int)devinfo.hardware_version);



	//std::cout << "abt to check lidar health...\n";
	 // check health...
	if (!checkRPLIDARHealth(drv)) {
		//std::cout << "lidar health check failed\n";
		goto on_finished;
	}

	//std::cout << "sending signal\n";
	signal(SIGINT, ctrlc);
	//std::cout << "abt to start motor\n";
	drv->startMotor();
	// start scan...
	drv->startScan(0, 1);

	//std::cout << "past starting scan\n";

	// median filter array
	LidarData lidarDatas[5];
	for (int i = 0; i < 5; i++) {
		lidarDatas[i] = { 2000, 2000, 2000, 2000 };
	}
	int dataIndex = 0;
	LidarData bestData;

	while (1) {
		//std::cout << "inside main loop\n";
		// reset matrix
		view = cv::Scalar::all(0);
		linesResult.clear();
		//std::cout << "past reset\n";

		rplidar_response_measurement_node_hq_t nodes[8192];
		size_t   count = _countof(nodes);

		op_result = drv->grabScanDataHq(nodes, count);

		if (IS_OK(op_result)) {
			//std::cout << "op_result is ok\n";
			drv->ascendScanData(nodes, count);
			for (int pos = 0; pos < (int)count; ++pos) {
				//std::cout << "in for loop \n";
				float a = nodes[pos].angle_z_q14 * 90.f / (1 << 14);
				a = 360 - a;
				// distance in mm
				int b = nodes[pos].dist_mm_q2 / 4.0f;
				// account for the lidar's tilt
				b = b * cos(lidarAngle);
				// quality from 0 to 100; lower is better
				float c = nodes[pos].quality;

				// filter out low quality points
				if (c > MIN_QUALITY) {
					// only use if it is within a certain angle
					if (a <= ANGULAR_RANGE/2 || a >= 360 - ANGULAR_RANGE/2) {
						int row = std::cos(_to_radians(a)) * b / MM_RESOLUTION; // y val (vert)
						int col = centerIndex - std::sin(_to_radians(a)) * b / MM_RESOLUTION; // x val (horiz)
						//std::cout << "row:" << row << "col:" << col << "\n";
						if (row < numRows && col < numCols) {
							view.at<unsigned char>(row, col) = (unsigned char)200;
						}
					}
				}
			}

			cv::imshow("lidar point map", view);

			//std::cout << "abt to call hough func...\n";
			//std::cout << view;
			cv::HoughLinesP(view, linesResult, 2, ANGLE_RESOLUTION* TWO_PIE / 360, 10, LINE_LENGTH * 3 / 4, 10);
			//std::cout << "called hough func for line segments ...\n";
			
			if (linesResult.size() > 0) {
				cv::Vec4i line = linesResult[0]; // default
				int index = 0;
				for (cv::Vec4i iter : linesResult) {
					/*cv::line(view, cv::Point(iter[0], iter[1]), cv::Point(iter[2], iter[3]),
					   cv::Scalar(255), 2, CV_AA);*/
					index++;

					double cur_line_len = std::sqrt((iter[0] - iter[2])*(iter[0] - iter[2]) + (iter[1] - iter[3])*(iter[1] - iter[3]));
					if (cur_line_len > LINE_LENGTH - ALLOWABLE_LEN_ERROR && cur_line_len < LINE_LENGTH + ALLOWABLE_LEN_ERROR) {
						line = iter;
					}
				}
				// display lines on image
				/*std::cout << line[0] << "," << line[1] << ","
					<< line[2] << "," << line[3] << ",";*/
				int newX1 = centerIndex - line[0];
				int newY1 = line[1];
				int newX2 = centerIndex - line[2];
				int newY2 = line[3];

				double lineLength = std::sqrt((newX1 - newX2) * (newX1 - newX2) + (newY1 - newY2) * (newY1 - newY2));

				cv::line(view, cv::Point(line[0], line[1]), cv::Point(line[2], line[3]),
					cv::Scalar(255), 2, CV_AA);
				cv::imshow("detected line", view);

				double centerX = (newX1*1.0 + newX2) / 2;
				double centerY = (newY1*1.0 + newY2) / 2;
				// distance to center, converted to inches
				double distance = std::sqrt(centerX * centerX + centerY * centerY) * MM_RESOLUTION / 25.4;
				// azimuth in radians. pointed to left of target results in positive azimuth, pointed to right of target results in negative azimuth
				double azimuth = std::atan2(centerX, centerY);

				// start calculations for relative angle to target, where 0 radians is right in front of the target
				double relAngle;
				if ((newX2 - newX1) * (newY2 - newY1) > 0) {
					relAngle = std::atan2(std::fabs(newY2 - newY1), std::fabs(newX2 - newX1)) + azimuth;

				}
				else {
					relAngle = std::atan2(std::fabs(newY2 - newY1), std::fabs(newX2 - newX1)) + (-azimuth);
					relAngle = -relAngle;
				}

				// calculate quality, lower quality is better!
				int quality = std::abs((int)(lineLength - LINE_LENGTH));

				// take the best quality out of the last 5 readings
				lidarDatas[dataIndex] = { azimuth, distance, relAngle, quality };
				dataIndex = (dataIndex + 1) % sizeof(lidarDatas);
				bestData = lidarDatas[0];
				for (int i = 0; i < sizeof(lidarDatas); i++) {
					if (bestData.quality > lidarDatas[i].quality) {
						bestData = lidarDatas[i];
					}
				}

				std::cout << "Relative angle to target=" << bestData.rel_angle * 360 / TWO_PIE << ", Azimuth=" << bestData.azimuth * 360 / TWO_PIE << ", ";
				std::cout << "Distance to center of target=" << bestData.distance;
				std::cout << ", Quality=" << bestData.quality << "\n";
			}
			else {
				cv::imshow("detected line", defaultImage);
			}
			cv::waitKey(0);

			if (ctrl_c_pressed) {
				break;
			}
		}
	}
	// end original code



	drv->stop();
	drv->stopMotor();
	// done!
on_finished:
	RPlidarDriver::DisposeDriver(drv);
	drv = NULL;
	return 0;
}
