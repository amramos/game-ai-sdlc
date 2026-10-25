class_name TextFit
extends RefCounted

## Whether a text fits a Label's box, measured the way Label lays it out: the font and size of its
## type role, its wrapping and edge-space trimming, line and paragraph spacing, `uppercase`,
## `max_lines_visible` and the margins of its `normal` stylebox.
##
## The box is the label's current size, so give the label the size its screen gives it and measure
## before setting the text: a Label grows to hold whatever text it is given, and the size read back
## afterwards would always fit. The label must be in the tree, so its theme resolves.


## True when `text` fits inside `label`'s box.
static func fits(label: Label, text: String) -> bool:
	return overflow(label, text) == Vector2.ZERO


## How far `text` spills past `label`'s box, in pixels on each axis; zero when it fits. Lines past
## `max_lines_visible` count as spilled even inside a tall box, since the label hides them.
static func overflow(label: Label, text: String) -> Vector2:
	var needed: Vector2 = measure(label, text)
	var spill: Vector2 = (needed - label.size).max(Vector2.ZERO)
	var hidden_lines: int = line_count(label, text) - label.max_lines_visible
	if label.max_lines_visible >= 0 and hidden_lines > 0:
		var font_size: int = label.get_theme_font_size(&"font_size")
		var line_height: float = label.get_theme_font(&"font").get_height(font_size)
		var line_step: float = line_height + label.get_theme_constant(&"line_spacing")
		spill.y = maxf(spill.y, hidden_lines * line_step)
	return spill


## The size `label` needs to show all of `text`, wrapped at its width when it wraps.
static func measure(label: Label, text: String) -> Vector2:
	var paragraphs: Array[TextParagraph] = _shape(label, text)
	# A blank line shapes to zero height, but Label still gives it a line of the font.
	var font_size: int = label.get_theme_font_size(&"font_size")
	var blank_line: float = label.get_theme_font(&"font").get_height(font_size)
	var width: float = 0.0
	var height: float = 0.0
	var lines: int = 0
	for paragraph: TextParagraph in paragraphs:
		for line: int in paragraph.get_line_count():
			var line_size: Vector2 = paragraph.get_line_size(line)
			width = maxf(width, line_size.x)
			height += line_size.y if line_size.y > 0.0 else blank_line
			lines += 1
	height += maxi(lines - 1, 0) * label.get_theme_constant(&"line_spacing")
	height += (paragraphs.size() - 1) * label.get_theme_constant(&"paragraph_spacing")
	return Vector2(width, height) + label.get_theme_stylebox(&"normal").get_minimum_size()


## How many lines `text` takes in `label`.
static func line_count(label: Label, text: String) -> int:
	var lines: int = 0
	for paragraph: TextParagraph in _shape(label, text):
		lines += paragraph.get_line_count()
	return lines


## One shaped paragraph per line of `text`, as Label splits it.
static func _shape(label: Label, text: String) -> Array[TextParagraph]:
	var font: Font = label.get_theme_font(&"font")
	var font_size: int = label.get_theme_font_size(&"font_size")
	var wrap_width: float = -1.0
	if label.autowrap_mode != TextServer.AUTOWRAP_OFF:
		var margins: Vector2 = label.get_theme_stylebox(&"normal").get_minimum_size()
		wrap_width = maxf(label.size.x - margins.x, 1.0)
	var shown: String = text.to_upper() if label.uppercase else text
	var paragraphs: Array[TextParagraph] = []
	for paragraph_text: String in shown.split("\n"):
		var paragraph: TextParagraph = TextParagraph.new()
		paragraph.break_flags = _break_flags(label.autowrap_mode) | label.autowrap_trim_flags
		paragraph.width = wrap_width
		paragraph.add_string(paragraph_text, font, font_size, label.language)
		paragraphs.append(paragraph)
	return paragraphs


## The line-break rules Label uses for each autowrap mode.
static func _break_flags(mode: TextServer.AutowrapMode) -> int:
	var flags: int = TextServer.BREAK_MANDATORY
	match mode:
		TextServer.AUTOWRAP_WORD_SMART:
			flags |= TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
		TextServer.AUTOWRAP_WORD:
			flags |= TextServer.BREAK_WORD_BOUND
		TextServer.AUTOWRAP_ARBITRARY:
			flags |= TextServer.BREAK_GRAPHEME_BOUND
	return flags
