import robomaster
from robomaster import robot

if __name__ == '__main__':
    # robomaster.config.LOCAL_IP_STR = "192.168.2.20"
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type='ap')

    version = ep_robot.get_version()
    print("Robot version: {0}".format(version))
    ep_robot.close()