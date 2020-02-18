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
#include "Socket.h"
#include "ServerSocket.h"
#include "SocketException.h"

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
   
   // ANGLE OF THE LIDAR FROM HORIZONTAL, in radians
   double lidarAngle = 0;
   // minimum quality of lidar data
   const int MIN_QUALITY = 10;
   // distance resolution of the hough line transform in mm
   const int MM_RESOLUTION = 20;
   // angle resolution of the hough line transform in deg
   const int ANGLE_RESOLUTION = 1;
   // radius in mm to consider for line detection
   const int RADIUS = 7000;
   // WIDTH OF THE LINE WE ARE LOOKING FOR, in PIXELS
   const int LINE_LENGTH = 1220/MM_RESOLUTION;
   // number of columns in the matrix
   int numCols = RADIUS * 2 / MM_RESOLUTION + 2;
   int numRows = RADIUS / MM_RESOLUTION + 1;
   // column index that is 0mm to MM_RESOLUTION mm
   int centerIndex = numCols / 2;
   // store the matrix to pass into hough transform function
   cv::Mat view(numRows, numCols, CV_8U, cv::Scalar(0));

   // store the lines found through hough transform
   std::vector<cv::Vec4i> linesResult;

	printf("Starting lidar!"
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

   //std::cout << "sending signal thing\n";
   signal(SIGINT, ctrlc);
   //std::cout << "abt to start motor\n";
	drv->startMotor();
	// start scan...
	drv->startScan(0, 1);
   
   //std::cout << "past starting scan\n";

   try {
      // listener socket
      ServerSocket server(1030);
      // make socket
      ServerSocket sock;
      // wait until server accepts socket 
      while (true) {
         if (server.accept(sock)) {
            break;
         }
      }

      LidarData lidarDatas[5];
      for (int i = 0; i < 5; i++) {
         lidarDatas[i] = { 2000, 2000, 2000, 2000 }; // default values
      }
      int dataIndex = 0;
      LidarData bestData;

      while (1) {
         //std::cout << "inside main loop\n";
         // reset matrix
         view = cv::Scalar::all(0);
         linesResult.clear();
         //houghLine[2] = 0;
         //std::cout << "past reset\n";

         rplidar_response_measurement_node_hq_t nodes[8192];
         size_t   count = _countof(nodes);

         op_result = drv->grabScanDataHq(nodes, count);

         if (IS_OK(op_result)) {
            //std::cout << "op_result is ok\n";
            drv->ascendScanData(nodes, count);
            for (int pos = 0; pos < (int)count; ++pos) {
               //std::cout << "in for loop \n";
               // angle TODO FLIP SOMEHOW?
               float a = nodes[pos].angle_z_q14 * 90.f / (1 << 14);
               a = 360 - a;
               // distance in mm
               int b = nodes[pos].dist_mm_q2 / 4.0f;
               // account for the lidar's tilt
               b = b * cos(lidarAngle);
               // quality from 0 to 100
               float c = nodes[pos].quality;/*
                                     printf("%s theta: %03.2f Dist: %08.2f Q: %d \n",
                                     (nodes[pos].flag & RPLIDAR_RESP_MEASUREMENT_SYNCBIT) ?"S ":"  ", a, b, c);*/
                                     // filter out low quality readings
               if (c > MIN_QUALITY) {
                  //std::cout << "within certain angle\n";
                  // only use if it is within a certain angle
                  //std::cout << a << ", ";
                  if (a <= 30 || a >= 330) {
                     int row = std::cos(a * TWO_PIE / 360) * b / MM_RESOLUTION; // y val (vert)
                     int col = centerIndex - std::sin(a * TWO_PIE / 360) * b / MM_RESOLUTION; // x val (horiz)
                     //std::cout << "row:" << row << "col:" << col << "\n";
                     if (row < numRows && col < numCols) {
                        view.at<unsigned char>(row, col) = (unsigned char)200;
                     }
                  }
               }
            }

          /*  cv::imwrite("doof.jpg", view);
            cv::imshow("points:", view);
            cv::waitKey(0);*/

            //std::cout << "abt to call hough func...\n";
            //std::cout << view;
            cv::HoughLinesP(view, linesResult, 3, ANGLE_RESOLUTION* TWO_PIE / 360, 10, 10, 864/MM_RESOLUTION);
            //std::cout << "called hough func for line segments ...\n";

            if (linesResult.size() > 0) {
               cv::Vec4i line = linesResult[0];
               for (cv::Vec4i iter : linesResult) {
                  double temp_line_len = std::sqrt((iter[0]-iter[2])*(iter[0]-iter[2]) + (iter[1]-iter[3])*(iter[1]-iter[3]));
                  if (temp_line_len > LINE_LENGTH - 20 && temp_line_len < LINE_LENGTH + 20) {
                     line = iter;
                  }
               }
               // display lines on image
               std::cout << line[0] << "," << line[1] << ","
                  << line[2] << "," << line[3] << ",";
               int newX1 = centerIndex - line[0];
               int newY1 = line[1];
               int newX2 = centerIndex - line[2];
               int newY2 = line[3];

               double lineLength = std::sqrt((newX1 - newX2) * (newX1 - newX2) + (newY1 - newY2) * (newY1 - newY2));

               /*cv::line(view, cv::Point(linesResult[0][0], linesResult[0][1]), cv::Point(linesResult[0][2], linesResult[0][3]), 
                  cv::Scalar(255), 2, CV_AA);
               cv::imshow("line:", view);
               cv::waitKey(0);*/
            
               double centerX = (newX1*1.0 + newX2) / 2;
               double centerY = (newY1*1.0 + newY2) / 2;
               double distance = std::sqrt(centerX * centerX + centerY * centerY);
               //std::cout << "orig_dist=" << distance << ",";
               // azimuth in radians. pointed to left of target results in positive azimuth, pointed to right of target results in negative azimuth
               double azimuth = std::atan2(centerX, centerY);
               
               // start calculations for relative angle to target, where 0 radians is right in front of the target

               double rel_angle;
               if ((newX2 - newX1) * (newY2 - newY1) > 0) {
                  rel_angle = std::atan2(std::fabs(newY2 - newY1), std::fabs(newX2 - newX1)) + azimuth;

               }
               else {
                  rel_angle = std::atan2(std::fabs(newY2 - newY1), std::fabs(newX2 - newX1)) + (-azimuth);
                  rel_angle = -rel_angle;
               }

               // calculate quality, lower quality is better!
               int quality = std::abs((int)(lineLength - LINE_LENGTH));

               // take the best quality out of the last 5 readings
               lidarDatas[dataIndex] = { azimuth, distance, rel_angle, quality };
               dataIndex = (dataIndex + 1) % 5;
               bestData = lidarDatas[0];
               for (int i = 0; i < 5; i++) {
                  if (bestData.quality > lidarDatas[i].quality) {
                     bestData = lidarDatas[i];
                  }
               }

               std::cout << "rel_angle:" << bestData.rel_angle * 360 / TWO_PIE << ",azimuth:" << bestData.azimuth * 360 / TWO_PIE << ",";
               std::cout << "distance to center of line seg:" << bestData.distance;
               std::cout << ",quality=" << bestData.quality << "\n";

               // send the best data to client
               try {
                  // send (azimuth,distance,rel_angle, quality)
                  sock << "("+ std::to_string(bestData.azimuth) + "," + std::to_string(bestData.distance*MM_RESOLUTION*INCH_PER_MM) + "," + std::to_string(bestData.rel_angle) + "," + std::to_string(bestData.quality)  + ")\n";
               }
               catch (SocketException e) {
                  std::cout << "lost connection with client, waiting for reconnection...\n";
                  while (true) {
                     if (ctrl_c_pressed) {
                        break;
                     }
                     if (server.accept(sock)) {
                        break;
                     }
                  }
               }


            }

            if (ctrl_c_pressed) {
               break;
            }
         }
      }
		// end original code


	}
	catch (SocketException & e) {
	   std::cout << "Exception was caught:" << e.description() << "\nExiting!";
	   return 1;
	}

	drv->stop();
	drv->stopMotor();
	// done!
on_finished:
	RPlidarDriver::DisposeDriver(drv);
	drv = NULL;
	return 0;
}
