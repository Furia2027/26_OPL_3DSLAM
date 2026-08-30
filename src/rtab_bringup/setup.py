import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'rtab_bringup'

# Base data files list
data_files = [
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    (os.path.join('share', package_name, 'gazebo'), glob('gazebo/*.sdf')),
    (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    (os.path.join('share', package_name, 'config'), glob('config/*.pgm'))
]

# Dynamically parse and add all files inside gazebo/models recursively
for root, dirs, files in os.walk('gazebo/models'):
    if files:
        target_dir = os.path.join('share', package_name, root)
        file_paths = [os.path.join(root, f) for f in files]
        data_files.append((target_dir, file_paths))

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='furia',
    maintainer_email='furia@todo.todo',
    description='RTAB Bringup Package',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
