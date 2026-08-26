"""Convert RTK NavSatFix (lat/lon) to map-frame coordinates.

The map frame is defined in map/georef.yaml: origin at the datum (SW corner
of the aerial), X = east, Y = north, meters. Datum parameters come from
config/gps_datum.yaml, which is GENERATED — to change the datum, edit
map/georef.yaml and run `python3 map/tools/update_georef.py`.

Publishes:
  /gps/map_pose   geometry_msgs/PoseStamped  robot position, meters E/N (frame_id: map)
  /gps/map_pixel  geometry_msgs/PointStamped pixel in washu_aerial.png (x right, y down)

Conversion is a local equirectangular approximation around the datum —
sub-centimeter error over this map's 1.4 km extent, fine for RTK work.
"""
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import PoseStamped, PointStamped

WGS84_A = 6378137.0
WGS84_E2 = 0.00669437999014


def local_radii(lat_rad):
    """WGS84 meridional (north) and prime-vertical (east) radii at lat."""
    s2 = math.sin(lat_rad) ** 2
    w = math.sqrt(1.0 - WGS84_E2 * s2)
    m = WGS84_A * (1.0 - WGS84_E2) / w ** 3
    n = WGS84_A / w
    return m, n


class GpsToMap(Node):
    def __init__(self):
        super().__init__('gps_to_map')
        self.declare_parameter('datum_lat', 38.6435)
        self.declare_parameter('datum_lon', -90.3161244)
        self.declare_parameter('datum_x', 0.0)
        self.declare_parameter('datum_y', 0.0)
        self.declare_parameter('fix_topic', '/fix')
        self.declare_parameter('resolution', 0.5)     # m/px of washu_aerial.png
        self.declare_parameter('image_height_px', 1860)

        self.lat0 = math.radians(self.get_parameter('datum_lat').value)
        self.lon0 = math.radians(self.get_parameter('datum_lon').value)
        self.x0 = self.get_parameter('datum_x').value
        self.y0 = self.get_parameter('datum_y').value
        self.res = self.get_parameter('resolution').value
        self.img_h = self.get_parameter('image_height_px').value
        self.r_north, r_prime = local_radii(self.lat0)
        self.r_east = r_prime * math.cos(self.lat0)

        fix_topic = self.get_parameter('fix_topic').value
        self.sub = self.create_subscription(NavSatFix, fix_topic, self.on_fix, 10)
        self.pose_pub = self.create_publisher(PoseStamped, '/gps/map_pose', 10)
        self.pixel_pub = self.create_publisher(PointStamped, '/gps/map_pixel', 10)
        self.get_logger().info(
            f'datum lat={math.degrees(self.lat0):.7f} lon={math.degrees(self.lon0):.7f}, '
            f'listening on {fix_topic}')

    def on_fix(self, fix: NavSatFix):
        if fix.status.status < 0:  # STATUS_NO_FIX
            return
        lat = math.radians(fix.latitude)
        lon = math.radians(fix.longitude)
        east = (lon - self.lon0) * self.r_east + self.x0
        north = (lat - self.lat0) * self.r_north + self.y0

        pose = PoseStamped()
        pose.header.stamp = fix.header.stamp
        pose.header.frame_id = 'map'
        pose.pose.position.x = east
        pose.pose.position.y = north
        pose.pose.orientation.w = 1.0
        self.pose_pub.publish(pose)

        px = PointStamped()
        px.header = pose.header
        px.point.x = east / self.res
        px.point.y = self.img_h - north / self.res
        self.pixel_pub.publish(px)


def main(args=None):
    rclpy.init(args=args)
    node = GpsToMap()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
