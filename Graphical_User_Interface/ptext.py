# ptext module: place this in your import directory.

# ptext.draw(text, pos=None, **options)

# Please see README.md for explanation of options.
# https://github.com/cosmologicon/pygame-text

from __future__ import division, print_function

from math import ceil, sin, cos, radians, exp
from collections import namedtuple
import pygame

DEFAULT_FONT_SIZE = 24
REFERENCE_FONT_SIZE = 100
DEFAULT_LINE_HEIGHT = 1.0
DEFAULT_PARAGRAPH_SPACE = 0.0
DEFAULT_FONT_NAME = None
FONT_NAME_TEMPLATE = "%s"
DEFAULT_COLOR = "white"
DEFAULT_BACKGROUND = None
DEFAULT_SHADE = 0
DEFAULT_OUTLINE_COLOR = "black"
DEFAULT_SHADOW_COLOR = "black"
OUTLINE_UNIT = 1 / 24
SHADOW_UNIT = 1 / 18
DEFAULT_ALIGN = "left"  # left, center, or right
DEFAULT_ANCHOR = 0, 0  # 0, 0 = top left ;  1, 1 = bottom right
DEFAULT_STRIP = True
ALPHA_RESOLUTION = 16
ANGLE_RESOLUTION_DEGREES = 3

AUTO_CLEAN = True
MEMORY_LIMIT_MB = 64
MEMORY_REDUCTION_FACTOR = 0.5

pygame.font.init()

# Options objects encapsulate the keyword arguments to functions that take a lot of keyword
# arguments.

# Options object base class. Subclass for Options objects specific to different functions.
# Specify valid fields in the _fields list. Unspecified fields default to None, unless otherwise
# specified in the _defaults list.
class _Options(object):
	_fields = ()
	_defaults = {}
	def __init__(self, **kwargs):
		fields = self._allfields()
		badfields = set(kwargs) - fields
		if badfields:
			raise ValueError("Unrecognized args: " + ", ".join(badfields))
		for field in fields:
			value = kwargs[field] if field in kwargs else self._defaults.get(field)
			setattr(self, field, value)
	@classmethod
	def _allfields(cls):
		return set(cls._fields) | set(cls._defaults)
	def update(self, **newkwargs):
		kwargs = { field: getattr(self, field) for field in self._allfields() }
		kwargs.update(**newkwargs)
		return kwargs
	def key(self):
		return tuple(getattr(self, field) for field in sorted(self._allfields()))
	def getsuboptions(self, optclass):
		return { field: getattr(self, field) for field in optclass._allfields() if hasattr(self, field) }


_default_surf_sentinel = ()

# Options argument for the draw function. Specifies both text styling and positioning.
class _DrawOptions(_Options):
	_fields = ("pos",
		"fontname", "fontsize", "sysfontname", "antialias", "bold", "italic", "underline",
		"color", "background",
		"top", "left", "bottom", "right", "topleft", "bottomleft", "topright", "bottomright",
		"midtop", "midleft", "midbottom", "midright", "center", "centerx", "centery",
		"width", "widthem", "lineheight", "pspace", "strip", "align",
		"owidth", "ocolor", "shadow", "scolor", "gcolor", "shade",
		"alpha", "anchor", "angle", "surf", "cache")
	_defaults = {
		"antialias": True, "alpha": 1.0, "angle": 0,
		"surf": _default_surf_sentinel, "cache": True }

	def __init__(self, **kwargs):
		_Options.__init__(self, **kwargs)
		self.expandposition()
		self.expandanchor()
		self.resolvesurf()

	# Expand each 2-element position specifier and overwrite the corresponding 1-element
	# position specifiers.
	def expandposition(self):
		if self.topleft: self.left, self.top = self.topleft
		if self.bottomleft: self.left, self.bottom = self.bottomleft
		if self.topright: self.right, self.top = self.topright
		if self.bottomright: self.right, self.bottom = self.bottomright
		if self.midtop: self.centerx, self.top = self.midtop
		if self.midleft: self.left, self.centery = self.midleft
		if self.midbottom: self.centerx, self.bottom = self.midbottom
		if self.midright: self.right, self.centery = self.midright
		if self.center: self.centerx, self.centery = self.center

	# Update the pos and anchor fields, if unspecified, to be specified by the positional
	# keyword arguments.
	def expandanchor(self):
		x, y = self.pos or (None, None)
		hanchor, vanchor = self.anchor or (None, None)
		if self.left is not None: x, hanchor = self.left, 0
		if self.centerx is not None: x, hanchor = self.centerx, 0.5
		if self.right is not None: x, hanchor = self.right, 1
		if self.top is not None: y, vanchor = self.top, 0
		if self.centery is not None: y, vanchor = self.centery, 0.5
		if self.bottom is not None: y, vanchor = self.bottom, 1
		if x is None:
			raise ValueError("Unable to determine horizontal position")
		if y is None:
			raise ValueError("Unable to determine vertical position")
		self.pos = x, y

		if self.align is None: self.align = hanchor
		if hanchor is None: hanchor = DEFAULT_ANCHOR[0]
		if vanchor is None: vanchor = DEFAULT_ANCHOR[1]
		self.anchor = hanchor, vanchor

	# Unspecified surf values default to the display surface.
	def resolvesurf(self):
		if self.surf is _default_surf_sentinel:
			self.surf = pygame.display.get_surface()

	def togetsurfoptions(self):
		return self.getsuboptions(_GetsurfOptions)


# Options for the layout function. By design, this has the same options as draw, although some of
# them are silently ignored.
class _LayoutOptions(_DrawOptions):
	def __init__(self, **kwargs):
		_Options.__init__(self, **kwargs)
		self.expandposition()
		self.expandanchor()		
		if self.lineheight is None: self.lineheight = DEFAULT_LINE_HEIGHT
		if self.pspace is None: self.pspace = DEFAULT_PARAGRAPH_SPACE

	def towrapoptions(self):
		return self.getsuboptions(_WrapOptions)

	def togetfontoptions(self):
		return self.getsuboptions(_GetfontOptions)


class _DrawboxOptions(_Options):
	_fields = (
		"fontname", "sysfontname", "antialias", "bold", "italic", "underline",
		"color", "background",
		"lineheight", "pspace", "strip", "align",
		"owidth", "ocolor", "shadow", "scolor", "gcolor", "shade",
		"alpha", "anchor", "angle", "surf", "cache")
	_defaults = {
		"antialias": True, "alpha": 1.0, "angle": 0, "anchor": (0.5, 0.5),
		"surf": _default_surf_sentinel, "cache": True }
	def __init__(self, **kwargs):
		_Options.__init__(self, **kwargs)
		if self.fontname is None: self.fontname = DEFAULT_FONT_NAME
		if self.lineheight is None: self.lineheight = DEFAULT_LINE_HEIGHT
		if self.pspace is None: self.pspace = DEFAULT_PARAGRAPH_SPACE

	def todrawoptions(self):
		return self.getsuboptions(_DrawOptions)

	def tofitsizeoptions(self):
		return self.getsuboptions(_FitsizeOptions)


class _GetsurfOptions(_Options):
	_fields = ("fontname", "fontsize", "sysfontname", "bold", "italic", "underline", "width",
		"widthem", "strip", "color", "background", "antialias", "ocolor", "owidth", "scolor",
		"shadow", "gcolor", "shade", "alpha", "align", "lineheight", "pspace", "angle", "cache")
	_defaults = { "antialias": True, "alpha": 1.0, "angle": 0, "cache": True }

	def __init__(self, **kwargs):
		_Options.__init__(self, **kwargs)
		if self.fontname is None: self.fontname = DEFAULT_FONT_NAME
		if self.fontsize is None: self.fontsize = DEFAULT_FONT_SIZE
		self.fontsize = int(round(self.fontsize))
		if self.align is None: self.align = DEFAULT_ALIGN
		if self.align in ["left", "center", "right"]:
			self.align = [0, 0.5, 1][["left", "center", "right"].index(self.align)]
		if self.lineheight is None: self.lineheight = DEFAULT_LINE_HEIGHT
		if self.pspace is None: self.pspace = DEFAULT_PARAGRAPH_SPACE
		self.color = _resolvecolor(self.color, DEFAULT_COLOR)
		self.background = _resolvecolor(self.background, DEFAULT_BACKGROUND)
		self.gcolor = _resolvecolor(self.gcolor, None)
		if self.shade is None: self.shade = DEFAULT_SHADE
		if self.shade:
			self.gcolor = _applyshade(self.gcolor or self.color, self.shade)
			self.shade = 0
		self.ocolor = None if self.owidth is None else _resolvecolor(self.ocolor, DEFAULT_OUTLINE_COLOR)
		self.scolor = None if self.shadow is None else _resolvecolor(self.scolor, DEFAULT_SHADOW_COLOR)

		self._opx = None if self.owidth is None else ceil(self.owidth * self.fontsize * OUTLINE_UNIT)
		self._spx = None if self.shadow is None else tuple(ceil(s * self.fontsize * SHADOW_UNIT) for s in self.shadow)
		self.alpha = _resolvealpha(self.alpha)
		self.angle = _resolveangle(self.angle)
		self.strip = DEFAULT_STRIP if self.strip is None else self.strip

	def towrapoptions(self):
		return self.getsuboptions(_WrapOptions)

	def togetfontoptions(self):
		return self.getsuboptions(_GetfontOptions)


class _WrapOptions(_Options):
	_fields = ("fontname", "fontsize", "sysfontname",
		"bold", "italic", "underline", "width", "widthem", "strip")

	def __init__(self, **kwargs):
		_Options.__init__(self, **kwargs)
		if self.widthem is not None and self.width is not None:
			raise ValueError("Can't set both width and widthem")

		if self.widthem is not None:
			self.width = self.widthem * REFERENCE_FONT_SIZE
			self.fontsize = REFERENCE_FONT_SIZE

		if self.strip is None:
			self.strip = DEFAULT_STRIP

	def togetfontoptions(self):
		return self.getsuboptions(_GetfontOptions)

	
class _GetfontOptions(_Options):
	_fields = ("fontname", "fontsize", "sysfontname", "bold", "italic", "underline")
	def __init__(self, **kwargs):
		_Options.__init__(self, **kwargs)
		if self.fontname is not None and self.sysfontname is not None:
			raise ValueError("Can't set both fontname and sysfontname")
		if self.fontname is None and self.sysfontname is None:
			fontname = DEFAULT_FONT_NAME
		if self.fontsize is None:
			self.fontsize = DEFAULT_FONT_SIZE
	def getfontpath(self):
		return self.fontname if self.fontname is None else FONT_NAME_TEMPLATE % self.fontname

class _FitsizeOptions(_Options):
	_fields = ("fontname", "sysfontname", "bold", "italic", "underline",
		"lineheight", "pspace", "strip")

	def togetfontoptions(self):
		return self.getsuboptions(_GetfontOptions)

	def towrapoptions(self):
		return self.getsuboptions(_WrapOptions)

_font_cache = {}
def getfont(**kwargs):
	options = _GetfontOptions(**kwargs)
	key = options.key()
	if key in _font_cache: return _font_cache[key]
	if options.sysfontname is not None:
		font = pygame.font.SysFont(options.sysfontname, options.fontsize, options.bold or False, options.italic or False)
	else:
		try:
			font = pygame.font.Font(options.getfontpath(), options.fontsize)
		except IOError:
			raise IOError("unable to read font filename: %s" % options.getfontpath())
	if options.bold is not None:
		font.set_bold(options.bold)
	if options.italic is not None:
		font.set_italic(options.italic)
	if options.underline is not None:
		font.set_underline(options.underline)
	_font_cache[key] = font
	return font

def wrap(text, **kwargs):
	options = _WrapOptions(**kwargs)
	font = getfont(**options.togetfontoptions())
	getwidth = lambda line: font.size(line)[0]
	# Apparently Font.render accepts None for the text argument, in which case it's treated as the
	# empty string. We match that behavior here.
	if text is None: text = ""
	paras = text.replace("\t", "    ").split("\n")
	lines = []
	for jpara, para in enumerate(paras):
		if options.strip:
			para = para.rstrip(" ")
		if options.width is None:
			lines.append((para, jpara))
			continue
		if not para:
			lines.append(("", jpara))
			continue
		# A break point is defined as any space character that immediately follows a non-space
		# character, or the end of the paragraph. These are the points that will be considered for
		# breaking a line off the front of the paragraph, although exactly how much whitespace goes
		# into the line depends on options.strip.
		
		# A valid break point is any break point such that breaking here will keep the width of the
		# line within options.width, with the exception that the first break point in the
		# paragraph is always valid. The goal of this algorithm is to find the last valid break
		# point.

		# Preserve paragraph leading spaces in all cases.
		lspaces = len(para) - len(para.lstrip(" "))
		# At any given time, a is the index of a known valid break point, and line = para[:a].
		a = para.index(" ", lspaces) if " " in para[lspaces:] else len(para)
		line = para[:a]
		while a + 1 < len(para):
			# b is the next break point, with bline the corresponding line to add.
			if " " not in para[a+1:]:
				b = len(para)
				bline = para
			else:
				# Find a space character that immediately follows a non-space character.
				b = para.index(" ", a + 1)
				while para[b-1] == " ":
					if " " in para[b+1:]:
						b = para.index(" ", b + 1)
					else:
						b = len(para)
						break
				bline = para[:b]
			bline = para[:b]
			if getwidth(bline) <= options.width:
				a, line = b, bline
			else:
				# Last vaild break point located.
				if not options.strip:
					# If options.strip is False, maintain as many spaces from after the break point
					# as will keep us under options.width.
					nspaces = len(para[a:]) - len(para[a:].lstrip(" "))
					for jspace in range(nspaces):
						nline = line + " "
						if getwidth(nline) > options.width:
							break
						line = nline
				lines.append((line, jpara))
				# Start the search over with the rest of the paragraph.
				para = para[a:].lstrip(" ")
				a = para.index(" ", 1) if " " in para[1:] else len(para)
				line = para[:a]
		# Handle the case of the first valid break point of the last line being the end of the line.
		# In this case there are no trailing spaces.
		if para:
			lines.append((line, jpara))
	return lines


# Return the largest integer in the range [xmin, xmax] such that f(x) is True.
def _binarysearch(f, xmin = 1, xmax = 256):
	if not f(xmin): return xmin
	if f(xmax): return xmax
	# xmin is the largest known value for which f(x) is True
	# xmax is the smallest known value for which f(x) is False
	while xmax - xmin > 1:
		x = (xmax + xmin) // 2
		if f(x):
			xmin = x
		else:
			xmax = x
	return xmin

_fit_cache = {}
def _fitsize(text, size, **kwargs):
	options = _FitsizeOptions(**kwargs)
	key = text, size, options.key()
	if key in _fit_cache: return _fit_cache[key]
	width, height = size
	def fits(fontsize):
		texts = wrap(text, fontsize=fontsize, width=width, **options.towrapoptions())
		font = getfont(fontsize=fontsize, **options.togetfontoptions())
		w = max(font.size(line)[0] for line, jpara in texts)
		linesize = font.get_linesize() * options.lineheight
		paraspace = font.get_linesize() * options.pspace
		h = int(round((len(texts) - 1) * linesize + texts[-1][1] * paraspace)) + font.get_height()
		return w <= width and h <= height
	fontsize = _binarysearch(fits)
	_fit_cache[key] = fontsize
	return fontsize

# Returns the color as a color RGB or RGBA tuple (i.e. 3 or 4 integers in the range 0-255)
# If color is None, fall back to the default. If default is also None, return None.
# Both color and default can be a list, tuple, a color name, an HTML color format string, a hex
# number string, or an integer pixel value. See pygame.Color constructor for specification.
def _resolvecolor(color, default):
	if color is None: color = default
	if color is None: return None
	try:
		return tuple(pygame.Color(color))
	except ValueError:
		return tuple(color)

def _applyshade(color, shade):
	f = exp(-0.4 * shade)
	r, g, b = [
		min(max(int(round((c + 50) * f - 50)), 0), 255)
		for c in color[:3]
	]
	return (r, g, b) + tuple(color[3:])

def _resolvealpha(alpha):
	if alpha >= 1:
		return 1
	return max(int(round(alpha * ALPHA_RESOLUTION)) / ALPHA_RESOLUTION, 0)

def _resolveangle(angle):
	if not angle:
		return 0
	angle %= 360
	return int(round(angle / ANGLE_RESOLUTION_DEGREES)) * ANGLE_RESOLUTION_DEGREES

# Return the set of points in the circle radius r, using Bresenham's circle algorithm
_circle_cache = {}
def _circlepoints(r):
	r = int(round(r))
	if r in _circle_cache:
		return _circle_cache[r]
	x, y, e = r, 0, 1 - r
	_circle_cache[r] = points = []
	while x >= y:
		points.append((x, y))
		y += 1
		if e < 0:
			e += 2 * y - 1
		else:
			x -= 1
			e += 2 * (y - x) - 1
	points += [(y, x) for x, y in points if x > y]
	points += [(-x, y) for x, y in points if x]
	points += [(x, -y) for x, y in points if y]
	points.sort()
	return points

# Rotate the given surface by the given angle, in degrees.
# If angle is an exact multiple of 90, use pygame.transform.rotate, otherwise fall back to
# pygame.transform.rotozoom.
def _rotatesurf(surf, angle):
	if angle in (90, 180, 270):
		return pygame.transform.rotate(surf, angle)
	else:
		return pygame.transform.rotozoom(surf, angle, 1.0)

# Apply the given alpha value to a copy of the Surface.
def _fadesurf(surf, alpha):
	surf = surf.copy()
	asurf = surf.copy()
	asurf.fill((255, 255, 255, int(round(255 * alpha))))
	surf.blit(asurf, (0, 0), None, pygame.BLEND_RGBA_MULT)
	return surf

def _istransparent(color):
	return len(color) > 3 and color[3] == 0

# Produce a 1xh Surface with the given color gradient.
_grad_cache = {}
def _gradsurf(h, y0, y1, color0, color1):
	key = h, y0, y1, color0, color1
	if key in _grad_cache:
		return _grad_cache[key]
	surf = pygame.Surface((1, h)).convert_alpha()
	r0, g0, b0 = color0[:3]
	r1, g1, b1 = color1[:3]
	for y in range(h):
		f = min(max((y - y0) / (y1 - y0), 0), 1)
		g = 1 - f
		surf.set_at((0, y), (
			int(round(g * r0 + f * r1)),
			int(round(g * g0 + f * g1)),
			int(round(g * b0 + f * b1)),
			0
		))
	_grad_cache[key] = surf
	return surf


_surf_cache = {}
_surf_tick_usage = {}
_surf_size_total = 0
_unrotated_size = {}
_tick = 0
def getsurf(text, **kwargs):
	global _tick, _surf_size_total
	options = _GetsurfOptions(**kwargs)
	key = text, options.key()

	if key in _surf_cache:
		_surf_tick_usage[key] = _tick
		_tick += 1
		return _surf_cache[key]
	texts = wrap(text, **options.towrapoptions())
	if options.angle:
		surf0 = getsurf(text, **options.update(angle = 0))
		surf = _rotatesurf(surf0, options.angle)
		_unrotated_size[(surf.get_size(), options.angle, text)] = surf0.get_size()
	elif options.alpha < 1.0:
		surf = _fadesurf(getsurf(text, **options.update(alpha = 1.0)), options.alpha)
	elif options._spx is not None:
		color = (0, 0, 0) if _istransparent(options.color) else options.color
		surf0 = getsurf(text, **options.update(background = (0, 0, 0, 0), color = color, shadow = None, scolor = None))
		ssurf = getsurf(text, **options.update(background = (0, 0, 0, 0), color = options.scolor, shadow = None, scolor = None, gcolor = None))
		w0, h0 = surf0.get_size()
		sx, sy = options._spx
		surf = pygame.Surface((w0 + abs(sx), h0 + abs(sy))).convert_alpha()
		surf.fill(options.background or (0, 0, 0, 0))
		dx, dy = max(sx, 0), max(sy, 0)
		surf.blit(ssurf, (dx, dy))
		x0, y0 = abs(sx) - dx, abs(sy) - dy
		if _istransparent(options.color):
			surf.blit(surf0, (x0, y0), None, pygame.BLEND_RGBA_SUB)
		else:
			surf.blit(surf0, (x0, y0))
	elif options._opx is not None:
		color = (0, 0, 0) if _istransparent(options.color) else options.color
		surf0 = getsurf(text, **options.update(color = color, ocolor = None, owidth = None))
		osurf = getsurf(text, **options.update(color = options.ocolor, ocolor = None, owidth = None, background = (0,0,0,0), gcolor = None))
		w0, h0 = surf0.get_size()
		opx = options._opx
		surf = pygame.Surface((w0 + 2 * opx, h0 + 2 * opx)).convert_alpha()
		surf.fill(options.background or (0, 0, 0, 0))
		for dx, dy in _circlepoints(opx):
			surf.blit(osurf, (dx + opx, dy + opx))
		if _istransparent(options.color):
			surf.blit(surf0, (opx, opx), None, pygame.BLEND_RGBA_SUB)
		else:
			surf.blit(surf0, (opx, opx))
	else:
		font = getfont(**options.togetfontoptions())
		color = options.color
		if options.gcolor is not None:
			color = 0, 0, 0
		# pygame.Font.render does not allow passing None as an argument value for background.
		if options.background is None or (len(options.background) > 3 and options.background[3] == 0) or options.gcolor is not None:
			lsurfs = [font.render(text, options.antialias, color).convert_alpha() for text, jpara in texts]
		else:
			lsurfs = [font.render(text, options.antialias, color, options.background).convert_alpha() for text, jpara in texts]
		if options.gcolor is not None:
			gsurf0 = _gradsurf(lsurfs[0].get_height(), 0.5 * font.get_ascent(), font.get_ascent(), options.color, options.gcolor)
			for lsurf in lsurfs:
				gsurf = pygame.transform.scale(gsurf0, lsurf.get_size())
				lsurf.blit(gsurf, (0, 0), None, pygame.BLEND_RGBA_ADD)
		if len(lsurfs) == 1 and options.gcolor is None:
			surf = lsurfs[0]
		else:
			w = max(lsurf.get_width() for lsurf in lsurfs)
			linesize = font.get_linesize() * options.lineheight
			parasize = font.get_linesize() * options.pspace
			ys = [int(round(k * linesize + jpara * parasize)) for k, (text, jpara) in enumerate(texts)]
			h = ys[-1] + font.get_height()
			surf = pygame.Surface((w, h)).convert_alpha()
			surf.fill(options.background or (0, 0, 0, 0))
			for y, lsurf in zip(ys, lsurfs):
				x = int(round(options.align * (w - lsurf.get_width())))
				surf.blit(lsurf, (x, y))
	if options.cache:
		w, h = surf.get_size()
		_surf_size_total += 4 * w * h
		_surf_cache[key] = surf
		_surf_tick_usage[key] = _tick
		_tick += 1
	return surf


# The actual position on the screen where the surf is to be blitted, rather than the specified
# anchor position.
def _blitpos(angle, pos, anchor, size, text):
	angle = _resolveangle(angle)
	x, y = pos
	sw, sh = size
	hanchor, vanchor = anchor
	if angle:
		w0, h0 = _unrotated_size[(size, angle, text)]
		S, C = sin(radians(angle)), cos(radians(angle))
		dx, dy = (0.5 - hanchor) * w0, (0.5 - vanchor) * h0
		x += dx * C + dy * S - 0.5 * sw
		y += -dx * S + dy * C - 0.5 * sh
	else:
		x -= hanchor * sw
		y -= vanchor * sh
	x = int(round(x))
	y = int(round(y))
	return x, y


def layout(text, **kwargs):
	options = _LayoutOptions(**kwargs)
	if options.angle != 0:
		raise ValueError("Nonzero angle not yet supported for ptext.layout")
	font = getfont(**options.togetfontoptions())
	texts = wrap(text, **options.towrapoptions())

	# TODO: the following is duplicated from getsurf
	rects = [pygame.Rect(0, 0, *font.size(text)) for text, jpara in texts]
	fh = font.get_height()
	fl = font.get_linesize()
	sw = max(rect.w for rect in rects)
	linesize = fl * options.lineheight
	parasize = fl * options.pspace
	ys = [int(round(k * linesize + jpara * parasize)) for k, (text, jpara) in enumerate(texts)]
	sh = ys[-1] + fl
	for y, rect in zip(ys, rects):
		rect.x = int(round(options.align * (sw - rect.w)))
		rect.y = y

	x0, y0 = _blitpos(options.angle, options.pos, options.anchor, (sw, sh), None)

	# Adjust the rects as necessary to account for outline and shadow.
	# TODO: the following is duplicated from _GetsurfOptions.__init__
	dx, dy = 0, 0
	if options.owidth is not None:
		opx = ceil(options.owidth * options.fontsize * OUTLINE_UNIT)
		dx, dy = max(dx, abs(opx)), max(dy, abs(opx))
	if options.shadow is not None:
		spx, spy = (ceil(s * options.fontsize * SHADOW_UNIT) for s in options.shadow)
		dx, dy = max(dx, -spx), max(dy, -spy)
	rects = [rect.move(x0 + dx, y0 + dy) for rect in rects]

	return font, [(text, rect) for (text, jpara), rect in zip(texts, rects)]


def draw(text, pos=None, **kwargs):
	options = _DrawOptions(pos = pos, **kwargs)
	tsurf = getsurf(text, **options.togetsurfoptions())
	pos = _blitpos(options.angle, options.pos, options.anchor, tsurf.get_size(), text)
	if options.surf is not None:
		options.surf.blit(tsurf, pos)
	if AUTO_CLEAN:
		clean()
	return tsurf, pos

def drawbox(text, rect, **kwargs):
	options = _DrawboxOptions(**kwargs)
	rect = pygame.Rect(rect)
	hanchor, vanchor = options.anchor
	x = rect.x + hanchor * rect.width
	y = rect.y + vanchor * rect.height
	fontsize = _fitsize(text, rect.size, **options.tofitsizeoptions())
	return draw(text, pos=(x,y), width=rect.width, fontsize=fontsize, **options.todrawoptions())

def clean():
	global _surf_size_total
	memory_limit = MEMORY_LIMIT_MB * (1 << 20)
	if _surf_size_total < memory_limit:
		return
	memory_limit *= MEMORY_REDUCTION_FACTOR
	keys = sorted(_surf_cache, key=_surf_tick_usage.get)
	for key in keys:
		w, h = _surf_cache[key].get_size()
		del _surf_cache[key]
		del _surf_tick_usage[key]
		_surf_size_total -= 4 * w * h
		if _surf_size_total < memory_limit:
			break


