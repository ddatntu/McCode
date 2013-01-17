
from xml.etree import ElementTree as ET
from math import sqrt, acos

# X3D properties taken from the Wikipedia example
# http://en.wikipedia.org/wiki/X3D
X3D_DOCTYPE = 'X3D PUBLIC "ISO//Web3D//DTD X3D 3.2//EN" "http://www.web3d.org/specifications/x3d-3.2.dtd"'

X3D_PROFILE = "Interchange"
X3D_VERSION = "3.2"
X3D_XMLNS   = "http://www.w3.org/2001/XMLSchema-instance"
X3D_SCHEMA  = " http://www.web3d.org/specifications/x3d-3.2.xsd "


class X3DWorld(object):
    def __init__(self):
        self.scene = Scene()
        self.world = X3D(scenes=[self.scene])

    def drawLine(self, points):
        self.scene.drawLine(points)

    def drawCircle(self, center=(0, 0, 0), radius=1):
        self.scene.drawCircle(center, radius)

    def dumps(self):
        return self.world.dumps()


def test():
    w = X3DWorld()

    lines = [
        [(-0.0239,-0.0245,0),(0.0239,-0.0245,0),(0.0239,0.0245,0),(-0.0239,0.0245,0),(-0.0239,-0.0245,0)],
        [(-0.0239,-0.0245,0.3048),(0.0239,-0.0245,0.3048),(0.0239,0.0245,0.3048),(-0.0239,0.0245,0.3048),(-0.0239,-0.0245,0.3048)],
        [(-0.0239,-0.0245,0),(-0.0239,-0.0245,0.3048)],
        [(0.0239,-0.0245,0),(0.0239,-0.0245,0.3048)],
        [(0.0239,0.0245,0),(0.0239,0.0245,0.3048)],
        [(-0.0239,0.0245,0),(-0.0239,0.0245,0.3048)]]

    map(w.drawLine, lines)

    file('test.x3d', 'w').write(w.dumps())


def dotProduct(p0, p1):
    return sum(a * x for a, x in zip(p0, p1))

def length(xs):
    return sqrt(sum(x**2 for x in xs))

def vectorAngle(v0, v1):
    ''' Calculate angle between vectors v0 and v1 '''
    return acos(dotProduct(v0, v1) / (length(v0) * length(v1)))

def pointAngle(p0, p1):
    ''' Calculate angle between the vectors (origo -> p0) and (p0 -> p1) '''
    return vectorAngle(p0, tuple(x-a for a,x in zip(p0, p1)))


class Node(object):
    def __init__(self):
        self._root = None

    def _addNode(self, childNode):
        self._root.append(childNode.getRoot())

    def getRoot(self):
        return self._root


class Shape(Node):
    def __init__(self, name, **kwargs):
        super(Shape, self).__init__()
        self._root = ET.Element('Shape')
        self._root.append(
            ET.Element(name, dict((str(k), str(v)) for k, v in kwargs.items()))
            )

    def addElem(self, name, **kwargs):
        self._root.getchildren()[0].append(
            ET.Element(name, dict((str(k), str(v)) for k, v in kwargs.items()))
            )


class Transform(Node):
    def __init__(self, translation=(0, 0, 0), rotation=(0, 0, 0, 0), shapes=()):
        super(Transform, self).__init__()
        self._root = ET.Element('Transform',
                                translation=' '.join(map(str, translation)),
                                rotation=' '.join(map(str, rotation)))
        map(self.addShape, shapes)

    def addShape(self, shape):
        ''' Extend with a scene that adheres to this tranformation '''
        self._addNode(shape)


class Scene(Node):
    def __init__(self, shapes=()):
        super(Scene, self).__init__()
        self._root = ET.Element('Scene')
        map(self.addShape, shapes)

    def addShape(self, shape):
        ''' Extend scene with a shape '''
        self._addNode(shape)

    def drawLine(self, points=(), thickness=1):
        ''' Draw a line from point (a, b, c) to point (x, y, z) '''
        points = map(tuple, points)
        line = Shape('IndexedLineSet',
                     coordIndex=' '.join('%i %i' % (i, i+1) for i in xrange(len(points)-1)),
                     colorIndex=' '.join('0'*(len(points)-1)*2))
        line.addElem('Color', color='1 1 1')
        line.addElem('Coordinate', point=' '.join('%s %s %s' % p for p in points))

        self._addNode(line)

    def drawCircle(self, center=(0, 0, 0), radius=1):
        ''' Draw a circle '''
        circle = Shape('Circle2D',
                       radius=radius)
        self._addNode(Transform(translation=center, shapes=[circle]))


class X3D(Node):
    def __init__(self, scenes=()):
        super(X3D, self).__init__()
        self._root = X3D.empty()
        map(self.addScene, scenes)

    @staticmethod
    def empty():
        ''' Construct empty xmlroot for X3D scene '''
        return ET.Element('X3D', {
            'profile': X3D_PROFILE,
            'version': X3D_VERSION,
            'xmlns:xsd': X3D_XMLNS,
            'xsd:noNamespaceSchemaLocation': X3D_SCHEMA
            })

    def dumps(self):
        ''' Dump contents as a string in X3D format '''
        xml = ''
        # Header
        xml += '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<!DOCTYPE %s>\n\n' % X3D_DOCTYPE
        # X3D body
        xml += ET.tostring(self._root)
        return xml

    def addScene(self, scene):
        ''' Extend X3D object with a scene '''
        self._addNode(scene)
