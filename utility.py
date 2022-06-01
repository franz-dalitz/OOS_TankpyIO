import math


class Camera:
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
		self.follow_speed_factor = 12

	def update(self, target=None):
		if target is not None:
			self.x += (target.x - self.x) / self.follow_speed_factor
			self.y += (target.y - self.y) / self.follow_speed_factor
		else:
			print('[CAMERA] Has no target')

	def project(self, entity, window):
		try:
			projected_x = entity.x - self.x + window.get_width() / 2
			projected_y = entity.y - self.y + window.get_height() / 2
			return projected_x, projected_y
		except Exception as error:
			print('[CAMERA] Failed to project')

	def set_target(self, target):
		self.target = target


def point_angle_degrees(x1, y1, x2, y2):
	radians = math.atan2(-(y2 - y1), x2 - x1)
	return math.degrees(radians)


def rotate_point_origin_angle(ox, oy, px, py, angle_degrees):
	angle = -math.radians(angle_degrees)
	qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
	qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
	return qx, qy
