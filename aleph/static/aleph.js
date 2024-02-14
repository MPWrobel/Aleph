document.addEventListener("alpine:init", () => {
	Alpine.data("table", (table, all_items) => ({
		all_items,
		selected_items: [],
		selected_count: `0 / ${all_items.length}`,
		all_selected: false,
		any_selected: false,
		items_vals: "",
		init() {
			this.$watch("selected_items", () => {
				this.items_vals = JSON.stringify({[table]: this.selected_items});

				const selected_len = this.selected_items.length;
				this.selected_count = `${selected_len} / ${all_items.length}`;
				this.all_selected = selected_len == this.all_items.length;
				this.any_selected = selected_len > 0;
			});
		}
	}));

	Alpine.bind("search", () => ({
		type: "search",
		"x-bind": "fetch",
		"x-model": "search",
		"hx-trigger": "input changed delay:100ms",
		"@keydown.document.slash"(e) {
			if (this.$el === document.activeElement) return;
			e.preventDefault();
			this.$el.focus();
		}
	}));

	Alpine.bind("sort", column => ({
		"x-bind": "fetch",
		'@click'() {
			if (this.$data.sort_by == column){
				this.$data.sort_desc = !this.$data.sort_desc;
			} else {
				this.$data.sort_desc = false;
				this.$data.sort_by = column;
			}
		},
		":class": `{
			sortable: true,
			sort: $data.sort_by === '${column}',
			sort_desc: $data.sort_by === '${column}' && $data.sort_desc
		}`
	}));

	Alpine.bind("fetch", () => ({
		":hx-vals"() {
			return JSON.stringify({
				search: this.$data.search,
				sort: this.$data.sort_by,
				desc: this.$data.sort_desc
			});
		},
		"hx-get": "",
		"hx-swap": "outerHTML",
		"hx-select": "table",
		"hx-target": "table"
	}));

	Alpine.bind("select_all", () => ({
		"x-effect"() {
			return this.$el.checked = this.$data.all_selected;
		},
		"@change"() {
			this.$data.selected_items = this.$el.checked ?
				this.$data.visible_items : [];
		}
	}));

	Alpine.bind("select_item", value => ({
		value,
		"x-model": "selected_items"
	}));

	Alpine.bind("action", url => ({
		"hx-get": url,
		":hx-vals": "items_vals"
	}));

	Alpine.bind("bulk_action", url => {
		const bind = {
			":class": "any_selected ? '' : 'disabled'",
		};
		if (url) {
			bind["hx-get"] = url;
			// bind["hx-push-url"] = "?delete";
			bind[":hx-vals"] = "items_vals";
		}
		return bind;
	});

	Alpine.bind("sticky", () => ({
		"x-data": "{sticky: $el.offsetTop, pageYOffset: window.pageYOffset}",
		":class": "{'sticky': pageYOffset > sticky}",
		"@scroll.window": "pageYOffset = window.pageYOffset"
	}));
});
