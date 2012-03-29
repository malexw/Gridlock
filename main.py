from sets import Set

# Scale
#OUTPUT_SCALE = 0.01
OUTPUT_SCALE = 1
#OUTPUT_SCALE = 0.23622

# Basic material and unit definitions
MATERIAL_THICKNESS = 12.7 # == 1/2"
UNIT_DEPTH = 152.4 # == 6"
UNIT_WIDTH_EXT = (482.6 + (2*MATERIAL_THICKNESS)) / 2 # 482.6 == 19"
UNIT_HEIGHT_EXT = 44.45 # 1.75" or 1U

# Feet
#FOOT_DEPTH = 25.4 # == 1"
FOOT_DEPTH = UNIT_DEPTH / 6

# Teeth
NUMBER_OF_TOP_TEETH = 4
NUMBER_OF_SIDE_TEETH = NUMBER_OF_TOP_TEETH - 1
NUMBER_OF_TEETH = NUMBER_OF_SIDE_TEETH + NUMBER_OF_TOP_TEETH
TEETH_DEPTH = (UNIT_DEPTH - (FOOT_DEPTH * 2)) / NUMBER_OF_TEETH

FACES_X = Set(['+X', '-X'])
FACES_Y = Set(['-Y', '+Y'])
FACES_Z = Set(['+Z', '-Z'])
FACES_X_AND_Y = FACES_X | FACES_Y
FACES_NEGATIVE_Z = Set(['-Z'])
FACES_POSITIVE_Z = Set(['+Z'])
FACES_ALL = FACES_X_AND_Y | FACES_NEGATIVE_Z | FACES_POSITIVE_Z

class Drawing:
  def __init__(self):
    self.triangles = []

  def add_cuboid(self, p1, p2, faces):
    n1 = Vector3(p1.x, p2.y, p1.z)
    n2 = p1
    n3 = Vector3(p2.x, p2.y, p1.z)
    n4 = Vector3(p2.x, p1.y, p1.z)
    n5 = p2
    n6 = Vector3(p2.x, p1.y, p2.z)
    n7 = Vector3(p1.x, p2.y, p2.z)
    n8 = Vector3(p1.x, p1.y, p2.z)
    self.add_cuboid_eight(n1, n2, n3, n4, n5, n6, n7, n8, faces)

  def add_cuboid_eight(self, p1, p2, p3, p4, p5, p6, p7, p8, faces):
    if '+Z' in faces:
      self.add_quad(p1, p2, p3, p4, Vector3(0, 0, 1))
    if '+X' in faces:
      self.add_quad(p3, p4, p5, p6, Vector3(1, 0, 0))
    if '-Z' in faces:
      self.add_quad(p5, p6, p7, p8, Vector3(0, 0, -1))
    if '-X' in faces:
      self.add_quad(p7, p8, p1, p2, Vector3(-1, 0, 0))
    if '+Y' in faces:
      self.add_quad(p7, p1, p5, p3, Vector3(0, 1, 0))
    if '-Y' in faces:
      self.add_quad(p2, p8, p4, p6, Vector3(0, -1, 0))

  def add_quad(self, p1, p2, p3, p4, norm):
    self.add_triangle(p1, p2, p3, norm)
    self.add_triangle(p3, p2, p4, norm)

  def add_triangle(self, p1, p2, p3, norm):
    t = Triangle()
    t.p1 = p1
    t.p2 = p2
    t.p3 = p3
    t.norm = norm
    self.triangles.append(t)

  def write_stl(self, file_handle):
    out.write("solid output\r\n")

    for triangle in self.triangles:
      triangle.write_stl(file_handle)

    out.write("endsolid output\r\n")

class Triangle:
  def __init__(self):
    self.p1 = Vector3(0,0,0)
    self.p2 = Vector3(0,0,0)
    self.p3 = Vector3(0,0,0)
    self.norm = Vector3(0,0,0)

  def as_string(self):
    return "1:<%s>, 2:<%s>, 3:<%s>, N:<%s>" % (self.p1.as_string(), self.p2.as_string(), self.p3.as_string(), self.norm.as_string())

  def write_stl(self, file_handle):
    file_handle.write("facet normal %s\r\n" % self.norm.as_string())
    file_handle.write("   outer loop\r\n")
    file_handle.write("      vertex %s\r\n" % self.p1.as_string())
    file_handle.write("      vertex %s\r\n" % self.p2.as_string())
    file_handle.write("      vertex %s\r\n" % self.p3.as_string())
    file_handle.write("   endloop\r\n")
    file_handle.write("endfacet\r\n")

class Vector3:
  def __init__(self, x, y, z):
    self.x = x
    self.y = y
    self.z = z

  def as_string(self):
    return "%s %s %s" % (self.x * OUTPUT_SCALE, self.y * OUTPUT_SCALE, self.z * OUTPUT_SCALE)

def add_side_panel(drawing, offsetx, height, depth):
  total_depth = UNIT_DEPTH * depth
  total_height = UNIT_HEIGHT_EXT * height
  # main body
  drawing.add_cuboid(Vector3(offsetx, 0, MATERIAL_THICKNESS), Vector3(total_depth + offsetx, MATERIAL_THICKNESS, total_height), FACES_X)
  drawing.add_cuboid(Vector3(offsetx, 0, 0), Vector3(total_depth + offsetx, MATERIAL_THICKNESS, MATERIAL_THICKNESS), FACES_X)

  # end pieces with feet
  for i in xrange(1, depth+1):
    foot1_x1 = offsetx + (UNIT_DEPTH * (i-1)) # left-most x coordinate of the left foot
    drawing.add_cuboid(Vector3(foot1_x1, 0, MATERIAL_THICKNESS), Vector3(foot1_x1 + FOOT_DEPTH, MATERIAL_THICKNESS, total_height), FACES_Y | FACES_NEGATIVE_Z)
    drawing.add_cuboid(Vector3(foot1_x1, 0, 0), Vector3(foot1_x1 + FOOT_DEPTH, MATERIAL_THICKNESS, MATERIAL_THICKNESS), FACES_Y | FACES_POSITIVE_Z | Set(['+X']))
    foot2_x2 = offsetx + (UNIT_DEPTH*i) # right-most x coordinate of the right foot
    drawing.add_cuboid(Vector3(foot2_x2 - FOOT_DEPTH, 0, MATERIAL_THICKNESS), Vector3(foot2_x2, MATERIAL_THICKNESS, total_height), FACES_Y | FACES_NEGATIVE_Z)
    drawing.add_cuboid(Vector3(foot2_x2 - FOOT_DEPTH, 0, 0), Vector3(foot2_x2, MATERIAL_THICKNESS, MATERIAL_THICKNESS), FACES_Y | FACES_POSITIVE_Z | Set(['-X']))

  # teeth
  # Add a set of teeth for every unit depth
  for i in xrange(1, depth+1):
    for j in xrange(1, NUMBER_OF_TOP_TEETH+1):
      tooth_x1 = offsetx + FOOT_DEPTH + TEETH_DEPTH + (UNIT_DEPTH * (i-1)) + ((TEETH_DEPTH*2) * (j-1))
      drawing.add_cuboid(Vector3(tooth_x1 - TEETH_DEPTH, 0, MATERIAL_THICKNESS), Vector3(tooth_x1, MATERIAL_THICKNESS, total_height), FACES_Y | FACES_Z)
      if j != NUMBER_OF_TOP_TEETH:
        drawing.add_cuboid(Vector3(tooth_x1, 0, total_height), Vector3(tooth_x1 + TEETH_DEPTH, MATERIAL_THICKNESS, total_height + MATERIAL_THICKNESS), FACES_X_AND_Y | FACES_NEGATIVE_Z)
        drawing.add_cuboid(Vector3(tooth_x1, 0, MATERIAL_THICKNESS), Vector3(tooth_x1 + TEETH_DEPTH, MATERIAL_THICKNESS, total_height), FACES_Y | FACES_POSITIVE_Z)


def add_top_panel(drawing, offsetx, width, depth):
  total_depth = UNIT_DEPTH * depth
  total_width = UNIT_WIDTH_EXT * width

  # end pieces
  #drawing.add_cuboid(Vector3(offsetx, 0, MATERIAL_THICKNESS), Vector3(total_depth + offsetx, MATERIAL_THICKNESS, total_width - MATERIAL_THICKNESS), FACES_X)

  # teeth
  for i in xrange(1, depth+1):
    for j in xrange(1, NUMBER_OF_TOP_TEETH+1):
      tooth_x1 = offsetx + FOOT_DEPTH + (UNIT_DEPTH * (i-1)) + ((TEETH_DEPTH*2) * (j-1))
      drawing.add_cuboid(Vector3(tooth_x1, 0, 0), Vector3(tooth_x1 + TEETH_DEPTH, MATERIAL_THICKNESS, MATERIAL_THICKNESS), FACES_X_AND_Y | FACES_POSITIVE_Z)
      drawing.add_cuboid(Vector3(tooth_x1, 0, total_width - MATERIAL_THICKNESS), Vector3(tooth_x1 + TEETH_DEPTH, MATERIAL_THICKNESS, total_width), FACES_X_AND_Y | FACES_NEGATIVE_Z)

      for k in xrange(1, width+1):
        block_z1 = (UNIT_WIDTH_EXT * (k-1))

        drawing.add_cuboid(Vector3(tooth_x1, 0, block_z1 + MATERIAL_THICKNESS), Vector3(tooth_x1 + TEETH_DEPTH, MATERIAL_THICKNESS, block_z1 + UNIT_WIDTH_EXT - MATERIAL_THICKNESS), FACES_Y)
        if k != width:
          drawing.add_cuboid(Vector3(tooth_x1, 0, block_z1 + UNIT_WIDTH_EXT - MATERIAL_THICKNESS), Vector3(tooth_x1 + TEETH_DEPTH, MATERIAL_THICKNESS, block_z1 + UNIT_WIDTH_EXT + MATERIAL_THICKNESS), FACES_Y)
        # add a quad to close off the body between the teeth
        # but don't add the quad in we're on the last tooth
        if j != NUMBER_OF_TOP_TEETH:
          if k == 1:
            drawing.add_cuboid(Vector3(tooth_x1 + TEETH_DEPTH, 0, block_z1 + MATERIAL_THICKNESS), Vector3(tooth_x1 + (2*TEETH_DEPTH), MATERIAL_THICKNESS, block_z1 + UNIT_WIDTH_EXT - MATERIAL_THICKNESS), FACES_Y | FACES_POSITIVE_Z)
          elif k == width:
            drawing.add_cuboid(Vector3(tooth_x1 + TEETH_DEPTH, 0, block_z1 + MATERIAL_THICKNESS), Vector3(tooth_x1 + (2*TEETH_DEPTH), MATERIAL_THICKNESS, block_z1 + UNIT_WIDTH_EXT - MATERIAL_THICKNESS), FACES_Y | FACES_NEGATIVE_Z)
          else:
            drawing.add_cuboid(Vector3(tooth_x1 + TEETH_DEPTH, 0, block_z1 + MATERIAL_THICKNESS), Vector3(tooth_x1 + (2*TEETH_DEPTH), MATERIAL_THICKNESS, block_z1 + UNIT_WIDTH_EXT - MATERIAL_THICKNESS), FACES_Y)

          if k != width:
            drawing.add_cuboid(Vector3(tooth_x1 + TEETH_DEPTH, 0, block_z1 + UNIT_WIDTH_EXT - MATERIAL_THICKNESS), Vector3(tooth_x1 + (2*TEETH_DEPTH), MATERIAL_THICKNESS, block_z1 + UNIT_WIDTH_EXT + MATERIAL_THICKNESS), FACES_Y)

  # quads above the feet
  for j in xrange(1, width+1):
    block_z1 = (UNIT_WIDTH_EXT * (j-1))
    drawing.add_cuboid(Vector3(offsetx, 0, block_z1 + MATERIAL_THICKNESS), Vector3(total_depth + offsetx, MATERIAL_THICKNESS, block_z1 + UNIT_WIDTH_EXT - MATERIAL_THICKNESS), FACES_X)

    for i in xrange(1, depth+1):
      foot_panel1_x1 = offsetx + (UNIT_DEPTH * (i-1))
      drawing.add_cuboid(Vector3(foot_panel1_x1, 0, block_z1 + MATERIAL_THICKNESS), Vector3(foot_panel1_x1 + FOOT_DEPTH, MATERIAL_THICKNESS, block_z1 + UNIT_WIDTH_EXT - MATERIAL_THICKNESS), FACES_Y | FACES_Z)
      foot_panel2_x2 = offsetx + (UNIT_DEPTH * i)
      drawing.add_cuboid(Vector3(foot_panel2_x2 - FOOT_DEPTH, 0, block_z1 + MATERIAL_THICKNESS), Vector3(foot_panel2_x2, MATERIAL_THICKNESS, block_z1 + UNIT_WIDTH_EXT - MATERIAL_THICKNESS), FACES_Y | FACES_Z)

      # Fills in holes between width units
      if j != width:
        drawing.add_cuboid(Vector3(foot_panel1_x1 + FOOT_DEPTH, 0, block_z1 + UNIT_WIDTH_EXT - MATERIAL_THICKNESS), Vector3(foot_panel2_x2 - FOOT_DEPTH, MATERIAL_THICKNESS, block_z1 + UNIT_WIDTH_EXT + MATERIAL_THICKNESS), FACES_X)


def add_simple_shelf(drawing, offsetx, width, height, depth):
  add_side_panel(drawing, offsetx, height, depth)
  add_side_panel(drawing, offsetx + (UNIT_DEPTH*depth) + MATERIAL_THICKNESS, height, depth)
  add_top_panel(drawing, offsetx + (((UNIT_DEPTH*depth) + MATERIAL_THICKNESS)*2), width, depth)
  #add_top_panel(drawing, offsetx, width, depth)

if __name__ == "__main__":
  d = Drawing()

  add_simple_shelf(d, 0, 1, 6, 1)
  add_simple_shelf(d, ((UNIT_DEPTH*1) + MATERIAL_THICKNESS) * 3, 1, 8, 1)
  add_simple_shelf(d, ((UNIT_DEPTH*1) + MATERIAL_THICKNESS) * 6, 1, 2, 1)
  add_simple_shelf(d, ((UNIT_DEPTH*1) + MATERIAL_THICKNESS) * 9, 2, 6, 2)

  out = open("out.stl", "w")
  d.write_stl(out)
  out.close()
