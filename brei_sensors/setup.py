from setuptools import find_packages, setup

package_name = 'brei_sensors'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='britt',
    maintainer_email='combrittho@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'brei_imgpub = brei_sensors.brei_imgpub:main',
            'brei_imu = brei_sensors.brei_imu:main',
            'brei_ultrasonic = brei_sensors.brei_ultrasonic:main',
        ],
    },
)
