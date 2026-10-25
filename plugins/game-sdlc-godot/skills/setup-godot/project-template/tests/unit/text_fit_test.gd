extends GutTest

## Every player-facing text fits its box at the native resolution (`game-ui`, commandment 8).
##
## Each screen that shows authored text adds its worst case here: instance the screen, take each
## label at the size the screen gives it, and check its longest string, in every language, with
## `TextFit` (`tests/support/text_fit.gd`). There is no exceptions list: a text that doesn't fit
## is a writer's trim, never a wider box.
##
## The tests below prove the helper on a plain Body label; screens add theirs after them.

const BOX: Vector2 = Vector2(200.0, 60.0)
const SHORT_TEXT: String = "Set sail"
const LONG_TEXT: String = (
	"A paragraph long enough to need far more than the two lines this box holds, because it keeps"
	+ " going well past the point where anyone would still be reading it."
)


func test_a_short_text_fits() -> void:
	var label: Label = _body_label(TextServer.AUTOWRAP_WORD_SMART)
	assert_eq(TextFit.overflow(label, SHORT_TEXT), Vector2.ZERO, "a short text fits a 200x60 box")


func test_a_long_text_overflows_the_height_of_a_wrapping_label() -> void:
	var label: Label = _body_label(TextServer.AUTOWRAP_WORD_SMART)
	var spill: Vector2 = TextFit.overflow(label, LONG_TEXT)
	assert_false(TextFit.fits(label, LONG_TEXT), "a long text doesn't fit a 200x60 box")
	assert_gt(spill.y, 0.0, "wrapped, it spills below the box (%s)" % spill)


func test_a_long_line_overflows_the_width_of_a_label_that_does_not_wrap() -> void:
	var label: Label = _body_label(TextServer.AUTOWRAP_OFF)
	var spill: Vector2 = TextFit.overflow(label, LONG_TEXT)
	assert_gt(spill.x, 0.0, "unwrapped, it spills past the right edge (%s)" % spill)


func _body_label(autowrap: TextServer.AutowrapMode) -> Label:
	var label: Label = Label.new()
	label.theme_type_variation = &"Body"
	label.autowrap_mode = autowrap
	add_child_autofree(label)
	label.size = BOX
	return label
