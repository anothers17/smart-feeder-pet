import pytest
import time
from simulator.virtual_device import VirtualDevice
from config.constants import Constants

def test_simulator_initial_state():
    """Test simulator starts with correct initial values."""
    device = VirtualDevice()
    assert device.food_mount == Constants.DEFAULT_FOOD_CAPACITY
    assert device.weight == 0.0
    assert device.servo_angle == Constants.SERVO_CLOSE

def test_simulator_feeding_logic():
    """Test that food transfers from storage to bowl when feeding."""
    device = VirtualDevice()
    device.food_mount = 100.0
    device.weight = 0.0
    device.servo_angle = Constants.SERVO_OPEN
    
    # Run simulation step
    device._simulate_feeding_behavior()
    
    assert device.weight > 0.0
    assert device.food_mount < 100.0
    assert device.weight + device.food_mount == pytest.approx(100.0)

def test_simulator_auto_stop():
    """Test that simulator stops feeding at target weight."""
    device = VirtualDevice()
    device.food_mount = 1000.0
    device.weight = Constants.SIMULATOR_MAX_BOWL_WEIGHT - 0.1
    device.servo_angle = Constants.SERVO_OPEN
    device.feeding_mode = "AUTO_90G"
    
    # Run simulation step
    device._simulate_feeding_behavior()
    
    # Should reach or exceed limit and close
    assert device.weight >= Constants.SIMULATOR_MAX_BOWL_WEIGHT
    assert device.servo_angle == Constants.SERVO_CLOSE

def test_simulator_eating_logic():
    """Test that bowl weight decreases when servo is closed (eating)."""
    device = VirtualDevice()
    device.weight = 50.0
    device.servo_angle = Constants.SERVO_CLOSE
    
    device._simulate_feeding_behavior()
    
    assert device.weight < 50.0
    assert device.weight >= 0.0
