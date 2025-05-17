#include "sdrplay_api.h"
#include <iostream>

// Arbitrarily set maximum number of devices.
constexpr unsigned int MAX_NUM_DEVICES = 5;

int main() {

    using namespace std;
    cout << "Looking for SDRplay devices...\n";

    // Open the SDRplay API and lock it for exclusive use while we look for devices.
    sdrplay_api_Open();  
    sdrplay_api_LockDeviceApi();

    // Find the number of available devices, and print the result to stdout.
    sdrplay_api_DeviceT devices[MAX_NUM_DEVICES];  
    unsigned int numDevices = 0;
    sdrplay_api_GetDevices(devices, &numDevices, MAX_NUM_DEVICES);
    cout << "Found " << numDevices << " SDRplay device(s)\n";

    // Unlock the API, then tidy up and close the API.
    sdrplay_api_UnlockDeviceApi();
    sdrplay_api_Close();
    
    return 0;
}
