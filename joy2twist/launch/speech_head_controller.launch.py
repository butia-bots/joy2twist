from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

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

    neck = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("fbot_hri_bringup"), 'neck.launch.py')
        ),
    )

    synthesizer_speech = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("fbot_hri_bringup"), 'synthesizer_speech.launch.py')
        
        ),
        launch_arguments={
            'use_remote': LaunchConfiguration("use_remote"),
        }.items()
    )

    actions = [
        declare_namespace_arg,
        joy_speech,
        joy,
        neck,
        synthesizer_speech

    ]

    return LaunchDescription(actions)