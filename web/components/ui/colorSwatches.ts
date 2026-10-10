import {
  Decoration,
  MatchDecorator,
  ViewPlugin,
  WidgetType,
  type DecorationSet,
  type EditorView,
  type ViewUpdate,
} from "@uiw/react-codemirror";

class ColorWidget extends WidgetType {
  constructor(readonly color: string) {
    super();
  }

  eq(other: ColorWidget) {
    return other.color === this.color;
  }

  toDOM(view: EditorView) {
    const input = document.createElement("input");
    input.type = "color";
    input.className = "color-swatch";
    input.value = this.color.toLowerCase();
    // "change", not "input": rewriting the text while dragging rebuilds this widget and closes the picker.
    input.addEventListener("change", () => {
      const from = view.posAtDOM(input);
      view.dispatch({ changes: { from, to: from + this.color.length, insert: input.value } });
    });
    return input;
  }

  ignoreEvent() {
    return true;
  }
}

const matcher = new MatchDecorator({
  regexp: /#[0-9a-fA-F]{6}\b/g,
  // Zero-length range: a widget spanning the match would replace the hex text.
  decorate: (add, from, _to, match) => add(from, from, Decoration.widget({ widget: new ColorWidget(match[0]), side: -1 })),
});

// Clickable color picker in front of every "#rrggbb" in the editor, like VS Code shows for CSS.
export const colorSwatches = ViewPlugin.fromClass(
  class {
    decorations: DecorationSet;
    constructor(view: EditorView) {
      this.decorations = matcher.createDeco(view);
    }
    update(update: ViewUpdate) {
      this.decorations = matcher.updateDeco(update, this.decorations);
    }
  },
  { decorations: (plugin) => plugin.decorations },
);
