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

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <vector>
#include "math.h"


#include "rplidar.h" //RPLIDAR standard sdk, all-in-one header

#include "opencv2/opencv.hpp"

#ifndef _countof
#define _countof(_Array) (int)(sizeof(_Array) / sizeof(_Array[0]))
#endif

#ifndef _to_radians
#define _to_radians(deg) (deg * 3.14159 / 180)
#endif

#ifdef _WIN32
#include <Windows.h>
#define delay(x)   ::Sleep(x)
#else
#include <unistd.h>
static inline void delay(_word_size_t ms){
	while (ms>=1000){
		usleep(1000*1000);
		ms-=1000;
	};
	if (ms!=0)
		usleep(ms*1000);
}
#endif

using namespace rp::standalone::rplidar;

bool checkRPLIDARHealth(RPlidarDriver * drv)
{
	u_result     op_result;
	rplidar_response_device_health_t healthinfo;


	op_result = drv->getHealth(healthinfo);
	if (IS_OK(op_result)) { // the macro IS_OK is the preperred way to judge whether the operation is succeed.
		printf("RPLidar health status : %d\n", healthinfo.status);
		if (healthinfo.status == RPLIDAR_STATUS_ERROR) {
			fprintf(stderr, "Error, rplidar internal error detected. Please reboot the device to retry.\n");
			// enable the following code if you want rplidar to be reboot by software
			// drv->reset();
			return false;
		} else {
			return true;
		}

	} else {
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



   //   try {
   // start original code...
   // fetch result and print it out...
   // minimum quality of lidar data
   const int MIN_QUALITY = 10;
   // distance resolution of the hough line transform in mm
   const int MM_RESOLUTION = 40;
   // angle resolution of the hough line transform in deg
   const int ANGLE_RESOLUTION = 1;
   // radius in mm to consider for line detection
   const int RADIUS = 6000;
   // number of columns in the matrix
   int numCols = RADIUS * 2 / MM_RESOLUTION + 2;
   int numRows = RADIUS / MM_RESOLUTION + 1;
   // column index that is 0mm to MM_RESOLUTION mm
   int centerIndex = numCols / 2;
   // store the matrix to pass into hough transform function
   cv::Mat view(numRows, numCols, CV_8UC1, 0);

   // store the lines found through hough transform
   std::vector<cv::Vec3i> linesResult;
   // store the best line found through hough
   cv::Vec3i houghLine;


	printf("Ultra simple LIDAR data grabber for RPLIDAR.\n"
		"Version: " RPLIDAR_SDK_VERSION "\n");

	// read serial port from the command line...
	if (argc > 1) opt_com_path = argv[1]; // or set to a fixed value: e.g. "com3" 

	// read baud rate from the command line if specified...
	if (argc > 2)
	{
		opt_com_baudrate = strtoul(argv[2], NULL, 10);
		useArgcBaudrate = true;
	}

	if (!opt_com_path) {
#ifdef _WIN32
		// use default com port
		opt_com_path = "\\\\.\\com57";
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
			std::cout << "insdie for loop on line 155" << baudrateArray[i] << "\n";
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
					std::cout << "delted drv on line 171\n";
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



	// check health...
	if (!checkRPLIDARHealth(drv)) {
		goto on_finished;
	}

   signal(2, ctrlc);//SIGINT, ctrlc);

	drv->startMotor();
	// start scan...
	drv->startScan(0, 1);

	//   try {
	// start original code...
	// fetch result and print it out...
	// minimum quality of lidar data
	//const int MIN_QUALITY = 10;
	//// distance resolution of the hough line transform in mm
	//const int MM_RESOLUTION = 40;
	//// angle resolution of the hough line transform in deg
	//const int ANGLE_RESOLUTION = 1;
	//// radius in mm to consider for line detection
	//const int RADIUS = 6000;
	//// number of columns in the matrix
	//int numCols = RADIUS*2 / MM_RESOLUTION + 2;
	//int numRows = RADIUS / MM_RESOLUTION + 1;
	//// column index that is 0mm to MM_RESOLUTION mm
	//int centerIndex = numCols/2;
	//// store the matrix to pass into hough transform function
	//cv::Mat view(numRows, numCols, CV_8UC1, 0);

	//// store the lines found through hough transform
	//std::vector<cv::Vec3i> linesResult;
	//// store the best line found through hough
	//cv::Vec3i houghLine;

   while (1) {
      std::cout << "inside main loop\n";
      // reset matrix
      view = cv::Scalar(0);
      linesResult.clear();
      houghLine[0] = 0;
      houghLine[1] = 0;
      houghLine[2] = 0;
      std::cout << "past reset\n";

      rplidar_response_measurement_node_hq_t nodes[8192];
      size_t   count = _countof(nodes);

      op_result = drv->grabScanDataHq(nodes, count);

      if (IS_OK(op_result)) {
         std::cout << "op_result is ok\n";
         drv->ascendScanData(nodes, count);
         for (int pos = 0; pos < (int)count; ++pos) {
            std::cout << "in for loop \n";
            // angle TODO FLIP SOMEHOW?
            float a = nodes[pos].angle_z_q14 * 90.f / (1 << 14);
            a = 360 - a;
            // distance in mm
            int b = nodes[pos].dist_mm_q2 / 4.0f;
            // quality from 0 to 100
            float c = nodes[pos].quality;/*
                                  printf("%s theta: %03.2f Dist: %08.2f Q: %d \n",
                                  (nodes[pos].flag & RPLIDAR_RESP_MEASUREMENT_SYNCBIT) ?"S ":"  ", a, b, c);*/
                                  // filter out low quality readings
            if (c < MIN_QUALITY) {
               // only use if it is within a certain angle
               if (a <= 30 || a >= 330) {
                  int row = std::cos(a * TWO_PIE / 360) * b / MM_RESOLUTION; // y val (vert)
                  int col = centerIndex - std::sin(a * TWO_PIE / 360) * b / MM_RESOLUTION; // x val (horiz)
                  view.at<int>(row, col) = 200;
                  std::cout << row << ", " << col << "\n";
               }
            }
         }


         std::cout << "abt to call hough func...\n";
         std::cout << view;
         //TODO CALL HOUGH TRANSFORM FUNCTION
         cv::HoughLines(view, linesResult, 1, ANGLE_RESOLUTION* TWO_PIE / 360, 6);
         std::cout << "called hough func...\n";
         if (linesResult.size() > 0) {
            // send data to client
            //try {
            houghLine = linesResult[0];
            for (int i = 0; i < linesResult.size(); i++) {//const cv::Vec3i& v : linesResult) {
               if (houghLine[2] < linesResult[0][2]) {
                  houghLine = linesResult[0];
               }
            }
            // houghLine now contains (r, theta, votes), and we need to convert it from its 
            // base image coordinate system to the lidar coordinate system.

            // first, convert the coordinate system to one centered at 0,0, with 0 deg pointing downward and positive angles in the counterclockwise direction
            houghLine[1] = 90 - houghLine[1];
            double x = -houghLine[0] * std::sin((double)houghLine[1]);
            double y = houghLine[0] * std::cos((double)houghLine[1]);
            houghLine[0] = (centerIndex * std::sin(_to_radians(houghLine[1]))) - houghLine[0];
            // solve for the new angle by doing some spicy maths from wolfram alpha
            // https://www.wolframalpha.com/input/?i=m%3Dx*cos%28b%29+%2B+y*sin%28b%29%2C+solve+for+b
            houghLine[1] = 2 * std::atan((y - std::sqrt(-(houghLine[0] * houghLine[0]) + x * x + y * y)) / (houghLine[0] + x));
            // houghLine now contains r,theta for the line, with (0,0) at the lidar with counterclockwise rotation

            std::cout << "r:" << houghLine[0] * MM_RESOLUTION << ",theta:" << houghLine[1] << "\n";


      }

         if (ctrl_c_pressed) {
            break;
         }
      }
   }
		// end original code


		//}
		//catch (SocketException & e) {
		//   std::cout << "Exception was caught:" << e.description() << "\nExiting!";
		//   return 1;
		//}

		drv->stop();
		drv->stopMotor();
		// done!
on_finished:
		RPlidarDriver::DisposeDriver(drv);
		drv = NULL;
		return 0;
}
