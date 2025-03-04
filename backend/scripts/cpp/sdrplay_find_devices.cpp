#include "sdrplay_api.h"
#include <iostream>

int main() {
    // Initialise an array to hold detected devices (up to 5, arbitrary)
    sdrplay_api_DeviceT devices [5];  
    // Initialise an integer to hold how many devices were detected.
    unsigned int numDevices = 0;
    
    sdrplay_api_Open();  
    sdrplay_api_GetDevices(devices, &numDevices, 10);
    std::cout << "Found " << numDevices << " SDRplay device(s)\n";
    sdrplay_api_Close();
    return 0;
}
