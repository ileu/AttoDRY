# This is a Python script for direct control of the AttoDRY2100 cryostat.
# It depends on the .dll files provided by AttoCube (AttoDRYLib.dll) which
# has to be referred to in the dll_directory variable. Not all functions
# are implemented in the given code, since control is still maintained with
# the attoDRY labview interface. All additional function names are found in the dll_list.txt
# file.
# You need to install the 2016 labview runtime engine. Additionally, the
# script will only work with a 32 bit python version.
#
# AttoDRY2100lib.py and PyAttoDRY2100.py are written by
# Christoph Murer
# Magnetism and interface Physics, ETH Zurich
# christoph.murer@mat.ethz.ch or chmurer@gmail.com
# script started on 04-Sep-2020
# inspired by the ANC350 scrips written by Rob Heath and Brian Schaefer (https://github.com/Laukei/pyanc350)

import AttoDRYlib as adryLib

# other import items:
import ctypes
from enum import IntEnum


# look at the header file to find the structure of a given function. This is just the implementation
# of temperature and field control without any further functionalities. All function descriptions are
# copied from the header files.


class Devices(IntEnum):
    """
    Enum for the different devices
    Setup versions:
    0: attoDRY1100
    1: attoDRY2100
    2: attoDRY800
    """

    ATTODRY1100 = 0
    ATTODRY2100 = 1
    ATTODRY800 = 2


class AttoDRY:
    def __init__(self, setup_version: Devices, com_port):
        self.setup_version = setup_version
        self.com_port = com_port

    def begin(self):
        """
        Starts the server that communicates with the attoDRY and loads the software
        for the device specified by <B> Device </B>. This VI needs to be run before
        commands can be sent or received. The <B>UI Queue</B> is an event queue for
        updating the GUI. It should not be used when calling the function from a
        DLL.
        Setup versions:
        0: attoDRY1100
        1: attoDRY2100
        2: attoDRY800
        """
        c = ctypes.c_uint16(self.setup_version)
        adryLib.begin(c.value)

    def Connect(self):
        """
        Connects to the attoDRY using the specified COM Port
        """
        COMPort = self.com_port.encode("utf-8")
        adryLib.Connect(ctypes.c_char_p(COMPort).value)

    def Disconnect(self):
        """
        Disconnects from the attoDRY, if already connected. This should be run
        before the <B>end.vi</B>
        """
        adryLib.Disconnect()

    def end(self):
        """
        Stops the server that is communicating with the attoDRY. The
        <B>Disconnect.vi</B> should be run before this. This VI should be run
        before closing your program.
        """

        if self.isDeviceConnected():
            self.Disconnect()

        adryLib.end()

    def Cancel(self):
        """
        Sends a 'Cancel' Command to the attoDRY. Use this when you want to cancel
        an action or respond negatively to a pop-up.
        """
        adryLib.Cancel()

    def Confirm(self):
        """
        Sends a 'Confirm' command to the attoDRY. Use this when you want to respond
        positively to a pop-up.
        """
        adryLib.Confirm()

    def getActionMessage(self, length=500):
        """
        Gets the current action message. If an action is being performed, it will
        be shown here. It is similar to the pop-ups on the display.
        """
        ActionMessage = ctypes.create_string_buffer(length)
        c_length = ctypes.c_int(length)
        adryLib.getAttodryErrorMessage(ctypes.byref(ActionMessage), c_length)
        return ActionMessage.value.decode("utf-8")

    def getAttodryErrorMessage(self, length=500):
        """
        Returns the current error message with length 500; Change that if characters are missing
        Too long should not be a problem(?)
        """
        ErrorStatus = ctypes.create_string_buffer(length)
        c_length = ctypes.c_int(length)
        adryLib.getAttodryErrorMessage(ctypes.byref(ErrorStatus), c_length)
        return ErrorStatus.value.decode("utf-8")

    def getAttodryErrorStatus(self):
        """
        Returns the current error code
        """
        ErrorCode = ctypes.c_int()
        adryLib.getAttodryErrorStatus(ctypes.byref(ErrorCode))
        return ErrorCode.value

    def isControllingField(self):
        """
        Returns 'True' if magnetic filed control is active. This is true when the
        magnetic field control icon on the touch screen is orange, and false when
        the icon is white.
        """
        ControllingField = ctypes.c_int()
        adryLib.isControllingField(ctypes.byref(ControllingField))
        return ControllingField.value

    def isControllingTemperature(self):
        """
        Returns 'True' if temperature control is active. This is true when the
        temperature control icon on the touch screen is orange, and false when the
        icon is white.
        """
        ControllingTemperature = ctypes.c_int()
        adryLib.isControllingTemperature(ctypes.byref(ControllingTemperature))
        return ControllingTemperature.value

    def isPersistentModeSet(self):
        """
        Checks to see if persistant mode is set for the magnet. Note: this shows if
        persistant mode is set, it does not show if the persistant switch heater is
        on. The heater may be on during persistant mode when, for example, changing
        the field.
        """
        PersistentMode = ctypes.c_int()
        adryLib.isPersistentModeSet(ctypes.byref(PersistentMode))
        return PersistentMode.value

    def isDeviceInitialised(self):
        """
        Checks to see if the attoDRY has initialised. Use this VI after you have
        connected and before sending any commands or getting any data from the
        attoDRY
        """
        DeviceInitialised = ctypes.c_int()
        adryLib.isDeviceInitialised(ctypes.byref(DeviceInitialised))
        return DeviceInitialised.value

    def isDeviceConnected(self):
        """
        Checks to see if the attoDRY is connected. Returns True if connected.
        """
        DeviceConnected = ctypes.c_int()
        adryLib.isDeviceConnected(ctypes.byref(DeviceConnected))
        return DeviceConnected.value

    def toggleMagneticFieldControl(self):
        """
        Toggles persistant mode for magnet control. If it is enabled, the switch
        heater will be turned off once the desired field is reached. If it is not,
        the switch heater will be left on.
        """
        adryLib.toggleMagneticFieldControl()

    def togglePersistentMode(self):
        """
        Starts and stops the pump. If the pump is running, it will stop it. If the
        pump is not running, it will be started.
        """
        adryLib.togglePersistentMode()

    def toggleSampleTemperatureControl(self):
        """
        This command only toggles the sample temperature controller. It does not
        pump the volumes etc. Use  <B>toggleFullTemperatureControl.vi</B> for
        behaviour like the temperature control icon on the touch screen.
        """
        adryLib.toggleSampleTemperatureControl()

    def toggleFullTemperatureControl(self):
        """
        This command only toggles the sample temperature controller. It does not
        pump the volumes etc. Use  <B>toggleFullTemperatureControl.vi</B> for
        behaviour like the temperature control icon on the touch screen.
        """
        adryLib.toggleFullTemperatureControl()

    def goToBaseTemperature(self):
        """
        Initiates the "Base Temperature" command, as on the touch screen
        """
        adryLib.goToBaseTemperature()

    def get4KStageTemperature(self):
        """
        Gets the current magnetic fiel
        """
        StageTemperature = ctypes.c_float()
        adryLib.get4KStageTemperature(ctypes.byref(StageTemperature))
        return StageTemperature.value

    def getMagneticField(self):
        """
        Gets the current magnetic fiel
        """
        MagneticField = ctypes.c_float()
        adryLib.getMagneticField(ctypes.byref(MagneticField))
        return MagneticField.value

    def getMagneticFieldSetPoint(self):
        """
        Gets the current magnetic field set point
        """
        MagneticField = ctypes.c_float()
        adryLib.getMagneticFieldSetPoint(ctypes.byref(MagneticField))
        return MagneticField.value

    def getSampleTemperature(self):
        """
        Gets the sample temperature in Kelvin. This value is updated whenever a
        status message is received from the attoDRY.
        """
        Temperature = ctypes.c_float()
        adryLib.getSampleTemperature(ctypes.byref(Temperature))
        return Temperature.value

    def getUserTemperature(self):
        """
        Gets the user set point temperature, in Kelvin. This value is updated
        whenever a status message is received from the attoDRY.
        """
        Temperature = ctypes.c_float()
        adryLib.getUserTemperature(ctypes.byref(Temperature))
        return Temperature.value

    def setUserMagneticField(self, magnetic_field):
        """
        Sets the user magntic field. This is used as the set point when field
        control is active
        """
        adryLib.setUserMagneticField(ctypes.c_float(magnetic_field))

    def setUserTemperature(self, temperature):
        """
        Sets the user temperature. This is the temperature used when temperature
        control is enabled.
        """
        adryLib.setUserTemperature(ctypes.c_float(temperature))

    ##################################################################################
    # Functions below this line were not tested!
    # TODO: test the following functions
    ##################################################################################

    def downloadSampleTemperatureSensorCalibrationCurve(self, savepath):
        """
        Starts the download of the <B>Sample Temperature Sensor Calibration
        Curve</B>. The curve will be saved to <B>Save Path</B>
        """
        Savepath = savepath.encode("utf-8")
        adryLib.downloadSampleTemperatureSensorCalibrationCurve(
            ctypes.c_char_p(Savepath).value
        )

    def downloadTemperatureSensorCalibrationCurve(self, user_curve_number, savepath):
        """
        Starts the download of the Temperature Sensor Calibration Curve at <b>User
        Curve Number</B> on the temperature monitor. The curve will be saved to
        <B>Path</B>
        """
        Savepath = savepath.encode("utf-8")
        adryLib.downloadTemperatureSensorCalibrationCurve(
            ctypes.c_int(user_curve_number), ctypes.c_char_p(Savepath).value
        )

    def getDerivativeGain(self):
        """
        Gets the Derivative gain. The gain retrieved depends on which heater is
        active:
        - If no heaters are on or the sample heater is on, the <B>Sample Heater</B>
        gain is returned
        - If the VTI heater is on and a sample temperature sensor is connected, the
        <B>VTI Heater</B> gain is returned
        - If the VTI heater is on and no sample temperature sensor is connected,
        the <B>Exchange Heater</B> gain is returned
        """
        DerivativeGain = ctypes.c_float()
        adryLib.getDerivativeGain(ctypes.byref(DerivativeGain))
        return DerivativeGain.value

    def getIntegralGain(self):
        """
        Gets the Integral gain. The gain retrieved depends on which heater is
        active:
        - If no heaters are on or the sample heater is on, the <B>Sample Heater</B>
        gain is returned
        - If the VTI heater is on and a sample temperature sensor is connected, the
        <B>VTI Heater</B> gain is returned
        - If the VTI heater is on and no sample temperature sensor is connected,
        the <B>Exchange Heater</B> gain is returned
        """
        IntegralGain = ctypes.c_float()
        adryLib.getIntegralGain(ctypes.byref(IntegralGain))
        return IntegralGain.value

    def getProportionalGain(self):
        """
        Gets the Proportional gain. The gain retrieved depends on which heater is
        active:
        - If no heaters are on or the sample heater is on, the <B>Sample Heater</B>
        gain is returned
        - If the VTI heater is on and a sample temperature sensor is connected, the
        <B>VTI Heater</B> gain is returned
        - If the VTI heater is on and no sample temperature sensor is connected,
        the <B>Exchange Heater</B> gain is returned
        """
        ProportionalGain = ctypes.c_float()
        adryLib.getProportionalGain(ctypes.byref(ProportionalGain))
        return ProportionalGain.value

    def getSampleHeaterMaximumPower(self):
        """
        Gets the maximum power limit of the sample heater in Watts. This value, is
        the one stored in memory on the computer, not the one on the attoDRY. You
        should first use the appropriate <B>query VI</B> to request the value from
        the attoDRY.

        The output power of the heater will not exceed this value. It is stored in
        non-volatile memory, this means that the value will not be lost, even if
        the attoDRY is turned off.
        """
        SampleHeaterMaximumPower = ctypes.c_float()
        adryLib.getSampleHeaterMaximumPower(ctypes.byref(SampleHeaterMaximumPower))
        return SampleHeaterMaximumPower.value

    def getSampleHeaterPower(self):
        """
        Gets the current Sample Heater power, in Watts
        """
        SampleHeaterPower = ctypes.c_float()
        adryLib.getSampleHeaterPower(ctypes.byref(SampleHeaterPower))
        return SampleHeaterPower.value

    def getSampleHeaterResistance(self):
        """
        Gets the resistance of the sample heater in Ohms. This value, is the one
        stored in memory on the computer, not the one on the attoDRY. You should
        first use the appropriate <B>query VI</B> to request the value from the
        attoDRY.

        This value, along with the heater wire resistance, is used in calculating
        the output power of the heater. It is stored in non-volatile memory, this
        means that the value will not be lost, even if the attoDRY is turned off.

        Power = Voltage^2/((HeaterResistance + WireResistance)^2) *
        HeaterResistance
        """
        SampleHeaterResistance = ctypes.c_float()
        adryLib.getSampleHeaterResistance(ctypes.byref(SampleHeaterResistance))
        return SampleHeaterResistance.value

    def getSampleHeaterWireResistance(self):
        """
        Gets the resistance of the sample heater wires in Ohms. This value, is the
        one stored in memory on the computer, not the one on the attoDRY. You
        should first use the appropriate <B>query VI</B> to request the value from
        the attoDRY.

        This value, along with the heater resistance, is used in calculating the
        output power of the heater. It is stored in non-volatile memory, this means
        that the value will not be lost, even if the attoDRY is turned off.

        Power = Voltage^2/((HeaterResistance + WireResistance)^2) *
        HeaterResistance
        """
        SampleHeaterWireResistance = ctypes.c_float()
        adryLib.getSampleHeaterWireResistance(ctypes.byref(SampleHeaterWireResistance))
        return SampleHeaterWireResistance.value

    def getVtiHeaterPower(self):
        """
        Returns the VTI Heater power, in Watts
        """
        VtiHeaterPower = ctypes.c_float()
        adryLib.getVtiHeaterPower(ctypes.byref(VtiHeaterPower))
        return VtiHeaterPower.value

    def getVtiTemperature(self):
        """
        Returns the temperature of the VTI
        """
        VtiTemperature = ctypes.c_float()
        adryLib.getVtiTemperature(ctypes.byref(VtiTemperature))
        return VtiTemperature.value

    def isGoingToBaseTemperature(self):
        """
        Returns 'True' if the base temperature process is active. This is true when
        the base temperature button on the touch screen is orange, and false when
        the button is white.
        """
        GoingToBaseTemperature = ctypes.c_int()
        adryLib.isGoingToBaseTemperature(ctypes.byref(GoingToBaseTemperature))
        return GoingToBaseTemperature.value

    def isPumping(self):
        """
        Returns true if the pump is running
        """
        Pumping = ctypes.c_int()
        adryLib.isPumping(ctypes.byref(Pumping))
        return Pumping.value

    def isSampleExchangeInProgress(self):
        """
        Returns 'True' if the sample exchange process is active. This is true when
        the sample exchange button on the touch screen is orange, and false when
        the button is white.
        """
        SampleExchangeInProgress = ctypes.c_int()
        adryLib.isSampleExchangeInProgress(ctypes.byref(SampleExchangeInProgress))
        return SampleExchangeInProgress.value

    def isSampleHeaterOn(self):
        """
        Checks to see if the sample heater is on. 'On' is defined as PID control is
        active or a contant heater power is set.
        """
        SampleHeaterOn = ctypes.c_int()
        adryLib.isSampleHeaterOn(ctypes.byref(SampleHeaterOn))
        return SampleHeaterOn.value

    def isSampleReadyToExchange(self):
        """
        This will return true when the sample stick is ready to be removed or
        inserted.
        """
        SampleReadyToExchange = ctypes.c_int()
        adryLib.isSampleReadyToExchange(ctypes.byref(SampleReadyToExchange))
        return SampleReadyToExchange.value

    def isSystemRunning(self):
        """
        This will return true when the sample stick is ready to be removed or
        inserted.
        """
        SystemRunning = ctypes.c_int()
        adryLib.isSystemRunning(ctypes.byref(SystemRunning))
        return SystemRunning.value

    def isZeroingField(self):
        """
        This will return true when the sample stick is ready to be removed or
        inserted.
        """
        ZeroingField = ctypes.c_int()
        adryLib.isZeroingField(ctypes.byref(ZeroingField))
        return ZeroingField.value

    def lowerError(self):
        """
        Lowers any raised errors
        """
        adryLib.lowerError()

    def querySampleHeaterMaximumPower(self):
        """
        Requests the maximum power limit of the sample heater in Watts from the
        attoDRY. After running this command, use the appropriate <B>get VI</B> to
        get the value stored on the computer.

        The output power of the heater will not exceed this value. It is stored in
        non-volatile memory, this means that the value will not be lost, even if
        the attoDRY is turned off.
        """
        adryLib.querySampleHeaterMaximumPower()

    def querySampleHeaterResistance(self):
        """
        Requests the  resistance of the sample heater in Ohms from the attoDRY.
        After running this command, use the appropriate <B>get VI</B> to get the
        value stored on the computer.

        This value, along with the heater wire resistance, is used in calculating
        the output power of the heater. It is stored in non-volatile memory, this
        means that the value will not be lost, even if the attoDRY is turned off.

        Power = Voltage^2/((HeaterResistance + WireResistance)^2) *
        HeaterResistance
        """
        adryLib.querySampleHeaterResistance()

    def querySampleHeaterWireResistance(self):
        """
        Requests the  resistance of the sample wires heater in Ohms from the
        attoDRY. After running this command, use the appropriate <B>get VI</B> to
        get the value stored on the computer.

        This value, along with the heater resistance, is used in calculating the
        output power of the heater. It is stored in non-volatile memory, this means
        that the value will not be lost, even if the attoDRY is turned off.

        Power = Voltage^2/((HeaterResistance + WireResistance)^2) *
        HeaterResistance
        """
        adryLib.querySampleHeaterWireResistance()

    def setDerivativeGain(self, derivative_gain):
        """
        Sets the Derivative gain. The controller that is updated depends on which
        heater is active:
        - If no heaters are on or the sample heater is on, the <B>Sample Heater</B>
        gain is set
        - If the VTI heater is on and a sample temperature sensor is connected, the
        <B>VTI Heater</B> gain is set
        - If the VTI heater is on and no sample temperature sensor is connected,
        the <B>Exchange Heater</B> gain is set
        """
        adryLib.setDerivativeGain(ctypes.c_float(derivative_gain))

    def setIntegralGain(self, integral_gain):
        """
        Sets the Integral gain. The controller that is updated depends on which
        heater is active:
        - If no heaters are on or the sample heater is on, the <B>Sample Heater</B>
        gain is set
        - If the VTI heater is on and a sample temperature sensor is connected, the
        <B>VTI Heater</B> gain is set
        - If the VTI heater is on and no sample temperature sensor is connected,
        the <B>Exchange Heater</B> gain is set
        """
        adryLib.setIntegralGain(ctypes.c_float(integral_gain))

    def setProportionalGain(self, proportional_gain):
        """
        Sets the Proportional gain. The controller that is updated depends on which
        heater is active:
        - If no heaters are on or the sample heater is on, the <B>Sample Heater</B>
        gain is set
        - If the VTI heater is on and a sample temperature sensor is connected, the
        <B>VTI Heater</B> gain is set
        - If the VTI heater is on and no sample temperature sensor is connected,
        the <B>Exchange Heater</B> gain is set
        """
        adryLib.setProportionalGain(ctypes.c_float(proportional_gain))

    def setSampleHeaterMaximumPower(self, maximum_power):
        """
        Sets the maximum power limit of the sample heater in Watts. After running
        this command, use the appropriate <B>request</B> and <B>get</B> VIs to
        check the value was stored on the attoDRY.

        The output power of the heater will not exceed this value.

        It is stored in non-volatile memory, this means that the value will not be
        lost, even if the attoDRY is turned off. Note: the non-volatile memory has
        a specified life of 100,000 write/erase cycles, so you may need to be
        careful about how often you set this value.
        """
        adryLib.setSampleHeaterMaximumPower(ctypes.c_float(maximum_power))

    def setSampleHeaterWireResistance(self, wire_resistance):
        """
        Sets the resistance of the sample heater wires in Ohms. After running this
        command, use the appropriate <B>request</B> and <B>get</B> VIs to check the
        value was stored on the attoDRY.

        This value, along with the heater resistance, is used in calculating the
        output power of the heater. It is stored in non-volatile memory, this means
        that the value will not be lost, even if the attoDRY is turned off.

        Power = Voltage^2/((HeaterResistance + WireResistance)^2) *
        HeaterResistance

        It is stored in non-volatile memory, this means that the value will not be
        lost, even if the attoDRY is turned off. Note: the non-volatile memory has
        a specified life of 100,000 write/erase cycles, so you may need to be
        careful about how often you set this value.
        """
        adryLib.setSampleHeaterWireResistance(ctypes.c_float(wire_resistance))

    def setSampleHeaterPower(self, heater_power_w):
        """
        Sets the sample heater value to the specified value
        """
        adryLib.setSampleHeaterPower(ctypes.c_float(heater_power_w))

    def setSampleHeaterResistance(self, heater_resistance):
        """
        Sets the resistance of the sample heater in Ohms. After running this
        command, use the appropriate <B>request</B> and <B>get</B> VIs to check the
        value was stored on the attoDRY.

        This value, along with the heater wire resistance, is used in calculating
        the output power of the heater. It is stored in non-volatile memory, this
        means that the value will not be lost, even if the attoDRY is turned off.

        Power = Voltage^2/((HeaterResistance + WireResistance)^2) *
        HeaterResistance

        It is stored in non-volatile memory, this means that the value will not be
        lost, even if the attoDRY is turned off. Note: the non-volatile memory has
        a specified life of 100,000 write/erase cycles, so you may need to be
        careful about how often you set this value.
        """
        adryLib.setSampleHeaterResistance(ctypes.c_float(heater_resistance))

    def startLogging(self, savepath, time_selection, append):
        """
        Starts logging data to the file specifed by <B>Path</B>.

        If the file does not exist, it will be created.
        The TimeSelection is given as
        #define Enum__1Second 0
        #define Enum__5Seconds 1
        #define Enum__30Seconds 2
        #define Enum__1Minute 3
        #define Enum__5Minutes 4
        """
        Savepath = savepath.encode("utf-8")
        adryLib.startLogging(
            ctypes.c_char_p(Savepath).value,
            ctypes.c_int(time_selection).value,
            ctypes.c_int(append).value,
        )

    def startSampleExchange(self):
        """
        Starts the sample exchange procedure
        """
        adryLib.startSampleExchange()

    def stopLogging(self):
        """
        Stops logging data
        """
        adryLib.stopLogging()

    def sweepFieldToZero(self):
        """
        Initiates the "Zero Field" command, as on the touch screen
        """
        adryLib.sweepFieldToZero()

    def togglePump(self):
        """
        Starts and stops the pump. If the pump is running, it will stop it. If the
        pump is not running, it will be started.
        """
        adryLib.togglePump()

    def toggleStartUpShutdown(self):
        """
        Toggles the start-up/shutdown procedure. If the attoDRY is started up, the
        shut-down procedure will be run and vice versa
        """
        adryLib.toggleStartUpShutdown()

    def uploadSampleTemperatureCalibrationCurve(self, loadpath):
        """
        Starts the upload of a <B>.crv calibration curve file</B> to the <B>sample
        temperature sensor</B>
        """
        Loadpath = loadpath.encode("utf-8")
        adryLib.uploadSampleTemperatureCalibrationCurve(ctypes.c_char_p(Loadpath).value)

    def uploadTemperatureCalibrationCurve(self, loadpath, user_curve_number):
        """
        Starts the upload of a <B>.crv calibration curve file</B> to the specified
        <B>User Curve Number</B> on the temperature monitor. Use a curve number of
        1 to 8, inclusive
        """
        Loadpath = loadpath.encode("utf-8")
        adryLib.uploadTemperatureCalibrationCurve(
            ctypes.c_int(user_curve_number).value, ctypes.c_char_p(Loadpath).value
        )

    def setVTIHeaterPower(self, vti_heater_power_w):
        """
        AttoDRY_Interface_setVTIHeaterPower
        """
        adryLib.setVTIHeaterPower(ctypes.c_float(vti_heater_power_w))

    def queryReservoirTsetColdSample(self):
        """
        AttoDRY_Interface_queryReservoirTsetColdSample
        """
        adryLib.queryReservoirTsetColdSample()

    def getReservoirTsetColdSample(self):
        """
        AttoDRY_Interface_getReservoirTsetColdSample
        """
        ReservoirTsetColdSampleK = ctypes.c_float()
        adryLib.getReservoirTsetColdSample(ctypes.byref(ReservoirTsetColdSampleK))
        return ReservoirTsetColdSampleK.value

    def setReservoirTsetWarmMagnet(self, reservoir_tset_warm_magnet_w):
        """
        AttoDRY_Interface_setReservoirTsetWarmMagnet
        """
        adryLib.setReservoirTsetWarmMagnet(ctypes.c_float(reservoir_tset_warm_magnet_w))

    def setReservoirTsetColdSample(self, set_reservoir_tset_cold_sample_k):
        """
        AttoDRY_Interface_setReservoirTsetColdSample
        """
        adryLib.setReservoirTsetColdSample(
            ctypes.c_float(set_reservoir_tset_cold_sample_k)
        )

    def setReservoirTsetWarmSample(self, ReservoirTsetWarmSampleW):
        """
        AttoDRY_Interface_setReservoirTsetWarmSample
        """
        adryLib.setReservoirTsetWarmSample(ctypes.c_float(ReservoirTsetWarmSampleW))

    def queryReservoirTsetWarmSample(self):
        """
        AttoDRY_Interface_queryReservoirTsetWarmSample
        """
        adryLib.queryReservoirTsetWarmSample()

    def queryReservoirTsetWarmMagnet(self):
        """
        AttoDRY_Interface_queryReservoirTsetWarmMagnet
        """
        adryLib.queryReservoirTsetWarmMagnet()

    def getReservoirTsetWarmSample(self):
        """
        AttoDRY_Interface_getReservoirTsetWarmSample
        """
        ReservoirTsetWarmSampleK = ctypes.c_float()
        adryLib.getReservoirTsetWarmSample(ctypes.byref(ReservoirTsetWarmSampleK))
        return ReservoirTsetWarmSampleK.value

    def getReservoirTsetWarmMagnet(self):
        """
        AttoDRY_Interface_getReservoirTsetWarmMagnet
        """
        ReservoirTsetWarmMagnetK = ctypes.c_float()
        adryLib.getReservoirTsetWarmMagnet(ctypes.byref(ReservoirTsetWarmMagnetK))
        return ReservoirTsetWarmMagnetK.value

    def getCryostatInPressure(self):
        """
        ATTODRY2100 ONLY. Gets the pressure at the Cryostat Inlet
        """
        CryostatInPressureMbar = ctypes.c_float()
        adryLib.getCryostatInPressure(ctypes.byref(CryostatInPressureMbar))
        return CryostatInPressureMbar.value

    def getCryostatInValve(self):
        """
        ATTODRY2100 ONLY. Gets the current status of the Cryostat In valve.
        """
        valveStatus = ctypes.c_int()
        adryLib.getCryostatInValve(ctypes.byref(valveStatus))
        return valveStatus.value

    def getCryostatOutPressure(self):
        """
        Gets the Cryostat Outlet pressure
        """
        CryostatOutPressureMbar = ctypes.c_float()
        adryLib.getCryostatOutPressure(ctypes.byref(CryostatOutPressureMbar))
        return CryostatOutPressureMbar.value

    def getCryostatOutValve(self):
        """
        ATTODRY2100 ONLY. Gets the current status of the Cryostat Out valve.
        """
        valveStatus = ctypes.c_int()
        adryLib.getCryostatOutValve(ctypes.byref(valveStatus))
        return valveStatus.value

    def getDumpInValve(self):
        """
        ATTODRY2100 ONLY. Gets the current status of the Dump In volume valve.
        """
        valveStatus = ctypes.c_int()
        adryLib.getDumpInValve(ctypes.byref(valveStatus))
        return valveStatus.value

    def getDumpOutValve(self):
        """
        ATTODRY2100 ONLY. Gets the current status of the outer volume valve.
        """
        valveStatus = ctypes.c_int()
        adryLib.getDumpOutValve(ctypes.byref(valveStatus))
        return valveStatus.value

    def getDumpPressure(self):
        """
        ATTODRY2100 ONLY. Gets the pressure at the Dump
        """
        DumpPressureMbar = ctypes.c_float()
        adryLib.getDumpPressure(ctypes.byref(DumpPressureMbar))
        return DumpPressureMbar.value

    def getReservoirHeaterPower(self):
        """
        ATTODRY2100 ONLY. Gets the pressure at the Dump
        """
        ReservoirHeaterPowerW = ctypes.c_float()
        adryLib.getReservoirHeaterPower(ctypes.byref(ReservoirHeaterPowerW))
        return ReservoirHeaterPowerW.value

    def getReservoirTemperature(self):
        """
        ATTODRY2100 ONLY. Gets the pressure at the Dump
        """
        ReservoirTemperatureK = ctypes.c_float()
        adryLib.getReservoirTemperature(ctypes.byref(ReservoirTemperatureK))
        return ReservoirTemperatureK.value

    def toggleCryostatInValve(self):
        """
        ATTODRY2100 ONLY. Toggles the Cryostat In valve. If it is closed, it will
        open and if it is open, it will close.
        """
        adryLib.toggleCryostatInValve()

    def toggleCryostatOutValve(self):
        """
        ATTODRY2100 ONLY. Toggles the Cryostat Out valve. If it is closed, it will
        open and if it is open, it will close.
        """
        adryLib.toggleCryostatOutValve()

    def toggleDumpInValve(self):
        """
        ATTODRY2100 ONLY. Toggles the inner volume valve. If it is closed, it will
        open and if it is open, it will close.
        """
        adryLib.toggleDumpInValve()

    def toggleDumpOutValve(self):
        """
        ATTODRY2100 ONLY. Toggles the outer volume valve. If it is closed, it will
        open and if it is open, it will close.
        """
        adryLib.toggleDumpOutValve()

    def get40KStageTemperature(self):
        """
        ATTODRY1100 ONLY. Gets the current temperature of the 40K Stage, in Kelvin
        """
        StageTemperatureK = ctypes.c_float()
        adryLib.get40KStageTemperature(ctypes.byref(StageTemperatureK))
        return StageTemperatureK.value

    def getHeliumValve(self):
        """
        ATTODRY1100 ONLY. Gets the current status of the helium valve. True is
        opened, false is closed.
        """
        valveStatus = ctypes.c_int()
        adryLib.getHeliumValve(ctypes.byref(valveStatus))
        return valveStatus.value

    def getInnerVolumeValve(self):
        """
        ATTODRY1100 ONLY. Gets the current status of the inner volume valve. True
        is opened, false is closed.
        """
        valveStatus = ctypes.c_int()
        adryLib.getInnerVolumeValve(ctypes.byref(valveStatus))
        return valveStatus.value

    def getOuterVolumeValve(self):
        """
        ATTODRY1100 ONLY. Gets the current status of the outer volume valve. True
        is opened, false is closed.
        """
        valveStatus = ctypes.c_int()
        adryLib.getOuterVolumeValve(ctypes.byref(valveStatus))
        return valveStatus.value

    def getPressure(self):
        """
        ATTODRY1100 ONLY. Gets the current presure in the valve junction block, in
        mbar.
        """
        PressureMbar = ctypes.c_float()
        adryLib.getPressure(ctypes.byref(PressureMbar))
        return PressureMbar.value

    def getPumpValve(self):
        """
        ATTODRY1100 ONLY. Gets the current status of the pump valve. True is
        opened, false is closed.
        """
        valveStatus = ctypes.c_int()
        adryLib.getPumpValve(ctypes.byref(valveStatus))
        return valveStatus.value

    def getTurbopumpFrequency(self):
        """
        ATTODRY1100 ONLY. Gets the current frequency of the turbopump.
        """
        TurbopumpFrequencyHz = ctypes.c_float()
        adryLib.getTurbopumpFrequency(ctypes.byref(TurbopumpFrequencyHz))
        return TurbopumpFrequencyHz.value

    def isExchangeHeaterOn(self):
        """
        Checks to see if the exchange/vti heater is on. 'On' is defined as PID
        control is active or a constant heater power is set.
        """
        ExchangeHeaterStatus = ctypes.c_int()
        adryLib.isExchangeHeaterOn(ctypes.byref(ExchangeHeaterStatus))
        return ExchangeHeaterStatus.value

    def toggleExchangeHeaterControl(self):
        """
        This command only toggles the exchange/vti temperature controller. If a
        sample temperature sensor is connected, this will be controlled, otherwise
        the temperature of the exchange tube will be used
        """
        adryLib.toggleExchangeHeaterControl()

    def toggleHeliumValve(self):
        """
        ATTODRY1100 ONLY. Toggles the helium valve. If it is closed, it will open
        and if it is open, it will close.
        """
        adryLib.toggleHeliumValve()

    def toggleInnerVolumeValve(self):
        """
        ATTODRY1100 ONLY.
        Toggles the inner volume valve. If it is closed, it will open and if it is
        open, it will close.
        """
        adryLib.toggleInnerVolumeValve()

    def toggleOuterVolumeValve(self):
        """
        ATTODRY1100 ONLY. Toggles the outer volume valve. If it is closed, it will
        open and if it is open, it will close.
        """
        adryLib.toggleOuterVolumeValve()

    def togglePumpValve(self):
        """
        ATTODRY1100 ONLY. Toggles the pump valve. If it is closed, it will open and
        if it is open, it will close.
        """
        adryLib.togglePumpValve()

    def getBreakVac800Valve(self):
        """
        ATTODRY800 ONLY. Gets the current status of the BreakVacuum valve.
        """
        valveStatus = ctypes.c_int()
        adryLib.getTurbopumpFrequency(ctypes.byref(valveStatus))
        return valveStatus.value

    # TODO: Look at code below for the attoDry 800
    def toggleSampleSpace800Valve(self):
        """
        ATTODRY800 ONLY. Toggles the SampleSpace valve. If it is closed, it will
        open and if it is open, it will close.
        """

        adryLib.toggleSampleSpace800Valve()

    def getPump800Valve(self):
        """
        ATTODRY800 ONLY. Gets the current status of the Pump valve.
        """
        valveStatus = ctypes.c_int()
        adryLib.getPump800Valve(ctypes.byref(valveStatus))
        return valveStatus.value

    def getSampleSpace800Valve(self):
        """
        ATTODRY800 ONLY. Gets the current status of the SampleSpace valve.
        """
        valveStatus = ctypes.c_int()
        adryLib.getSampleSpace800Valve(ctypes.byref(valveStatus))
        return valveStatus.value

    def togglePump800Valve(self):
        """
        ATTODRY800 ONLY. Toggles the Pump valve. If it is closed, it will open and
        if it is open, it will close.
        """
        adryLib.togglePump800Valve()

    def toggleBreakVac800Valve(self):
        """
        ATTODRY800 ONLY. Toggles the BreakVacuum valve. If it is closed, it will
        open and if it is open, it will close.
        """
        adryLib.toggleBreakVac800Valve()

    def getPressure800(self):
        """
        ATTODRY800 ONLY. Gets the pressure at the Cryostat Inlet.
        """
        CryostatInPressureMbar = ctypes.c_float()
        adryLib.getPressure800(ctypes.byref(CryostatInPressureMbar))
        return CryostatInPressureMbar.value

    def GetTurbopumpFrequ800(self):
        """
        ATTODRY800 ONLY. Gets the current frequency of the turbopump.
        """
        TurbopumpFrequencyHz = ctypes.c_float()
        adryLib.GetTurbopumpFrequ800(ctypes.byref(TurbopumpFrequencyHz))
        return TurbopumpFrequencyHz.value
