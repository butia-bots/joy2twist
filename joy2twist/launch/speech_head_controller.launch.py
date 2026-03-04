from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    namespace = LaunchConfiguration("namespace")
    declare_namespace_arg = DeclareLaunchArgument(
        "namespace",
        default_value=EnvironmentVariable("ROBOT_NAMESPACE", default_value=""),
        description="Add namespace to all launched nodes.",
    )

    config_remote_arg = DeclareLaunchArgument(
        'use_remote',
        default_value='false',
        description="If should run the node on remote"
    )

    declare_use_neck_arg = DeclareLaunchArgument(
        'use_neck',
        default_value='true',
        description="If should launch the neck controller"
    )

    declare_use_speech_arg = DeclareLaunchArgument(
        'use_speech',
        default_value='true',
        description="If should launch the speech synthesizer"
    )

    joy_speech = Node(
        package="joy2twist",
        executable="joy_speech.py",
        emulate_tty="true",
        namespace=namespace,
        remappings=[("/diagnostics", "diagnostics")],
    )

    joy = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("joy2twist"), 'launch', 'gamepad_controller.launch.py')
        ),
    )

    neck = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("fbot_head"), 'launch', 'neck.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration("use_neck")),
    )

    synthesizer_speech = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("fbot_hri_bringup"), 'synthesizer_speech.launch.py')
        ),
        launch_arguments={
            'use_remote': LaunchConfiguration("use_remote"),
        }.items(),
        condition=IfCondition(LaunchConfiguration("use_speech")),
    )

    actions = [
        declare_namespace_arg,
        config_remote_arg,
        declare_use_neck_arg,
        declare_use_speech_arg,
        joy_speech,
        joy,
        neck,
        synthesizer_speech,
    ]

    return LaunchDescription(actions)