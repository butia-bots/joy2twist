from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import EnvironmentVariable, LaunchConfiguration

def generate_launch_description():
    namespace = LaunchConfiguration("namespace")
    declare_namespace_arg = DeclareLaunchArgument(
        "namespace",
        default_value=EnvironmentVariable("ROBOT_NAMESPACE", default_value=""),
        description="Add namespace to all launched nodes.",
    )

    joy_speech = Node(
        package="joy2twist",
        executable="joy_speech.py",
        emulate_tty="true",
        namespace=namespace,
        remappings=[("/diagnostics", "diagnostics")],
    )

    joy = Node(
        package="joy",
        executable="joy_node",
        emulate_tty="true",
        namespace=namespace,
        remappings=[("/diagnostics", "diagnostics")],
    )

    actions = [
        declare_namespace_arg,
        joy_speech,
        joy

    ]

    return LaunchDescription(actions)