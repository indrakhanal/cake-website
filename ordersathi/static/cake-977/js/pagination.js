
(function(root) {
	"use strict";
	var win = window,
		doc = document,
		body = doc.body;

	/**
     * Default configuration
     * @typ {Object}
     */
	var defaultConfig = {
		limit: 0,
		offset: 2,
		startPage: 1,
		hideDisabled: true,
		prevNext: true,
		prevText: "&lsaquo;",
		nextText: "&rsaquo;",
		firstLast: false,
		firstText: "&laquo;",
		lastText: "&raquo;",		
		ellipsisText: "&hellip;",
		hashString: "#",
		
		classes: {
			pager: "pg-pager",
			item: "pg-item",
			link: "pg-link",
			prev: "pg-prev",
			next: "pg-next",
			first: "pg-first",
			last: "pg-last",		
			active: "pg-active",
			disabled: "pg-disabled",
			ellipsis: "pg-ellipsis",
		}
	};

	/**
     * Check is item is object
     * @return {Boolean}
     */
	var isObject = function(val) {
		return Object.prototype.toString.call(val) === "[object Object]";
	};

	/**
     * Check is item is array
     * @return {Boolean}
     */
	var isArray = function(val) {
		return Array.isArray(val);
	};
	
	var closest = function(el, fn) {
		return el && el !== body && (fn(el) ? el : closest(el.parentNode, fn));
	};
	
	/**
     * Merge objects (reccursive)
     * @param  {Object} r
     * @param  {Object} t
     * @return {Object}
     */
	var extend = function(src, props) {
		for (var prop in props) {
			if (props.hasOwnProperty(prop)) {
				var val = props[prop];
				if (val && isObject(val)) {
					src[prop] = src[prop] || {};
					extend(src[prop], val);
				} else {
					src[prop] = val;
				}
			}
		}
		return src;
	};

	/**
     * Iterator helper
     * @param  {(Array|Object)}   arr     Any object, array or array-like collection.
     * @param  {Function}         fn      Callback
     * @param  {Object}           scope   Change the value of this
     * @return {Void}
     */
	var each = function(arr, fn, scope) {
		var n;
		if ( Number.isInteger(arr) ) {
			for (n = 0; n < arr; n++) {
				fn.call(scope, n + 1, n);
			}
		} else {
			if (isObject(arr)) {
				for (n in arr) {
					if (Object.prototype.hasOwnProperty.call(arr, n)) {
						fn.call(scope, arr[n], n);
					}
				}
			} else {
				for (n = 0; n < arr.length; n++) {
					fn.call(scope, arr[n], n);
				}
			}
		}
	};

	/**
     * Add event listener to target
     * @param  {Object} el
     * @param  {String} e
     * @param  {Function} fn
     */
	var on = function(el, e, fn) {
		el.addEventListener(e, fn, false);
	};

	/**
     * Create DOM element node
     * @param  {String}   a nodeName
     * @param  {Object}   b properties and attributes
     * @return {Object}
     */
	var createNode = function(a, b) {
		var d = doc.createElement(a);
		if (b && "object" == typeof b) {
			var e;
			for (e in b) {
				if ("html" === e) {
					d.innerHTML = b[e];
				} else {
					d.setAttribute(e, b[e]);
				}
			}
		}
		return d;
	};
	
	var getPage = function(e) {
		return parseInt(e.getAttribute("data-page"), 10);		
	};


	var Pager = function(config) {
		this.config = extend(defaultConfig, config);

		this.container = this.config.container;

		if (typeof this.container === "string") {
			this.container = document.querySelector(this.container);
		}
		
		if ( this.config.pages ) {
			this.totalPages = this.config.pages;
		}
		
		this.limit = this.config.limit;
		this.offset = this.config.offset;
		this.hideDisabled = this.config.hideDisabled;
		
		this.bindEvents();
		
		if ( this.config.startPage ) {
			this.goTo(this.config.startPage);
		}		
		
		var that = this;
		setTimeout(function() {
			that.emit("init", that.currentPage);
		}, 10);
	};
	
	Pager.prototype.bindEvents = function() {
		
		this.events = {
			click: this.click.bind(this)
		};
		
		on(this.container, "click", this.events.click);
	};
	
	Pager.prototype.click = function(e) {
		var that = this, target = e.target, o = that.config;
		
		var item = closest(target, function(node) {
			return node.item;
		});
		
		if ( item ) {
			e.preventDefault();
		
			if (item.ellipsis) {
				return;
			}
			
			that.goTo(parseInt(item.dataset.page, 10))
		}
	};	
	
	Pager.prototype.render = function(pages) {
		
		var that = this, o = that.config,
				node = document.createDocumentFragment();
		
		if ( pages ) {
			that.items = [];
			that.totalPages = pages;
			
			if ( that.currentPage > that.totalPages ) {
				that.currentPage = that.totalPages;
			}
		}
		
		if ( that.pager ) {
			that.pager.className = o.classes.pager;
		} else {
			that.pager = createNode("ul", {
				class: o.classes.pager
			});
		}
		
		var items = that.truncate();
		
		if ( that.hideDisabled && that.currentPage === 1 ) {
		} else {
		
			if ( o.firstLast ) {
				that.first = that.renderButton({
					class: o.classes.first,
					content: o.firstText,
					page: 1,
					nav: true,
					first: true
				});

				node.appendChild(that.first);
			}		

			if ( o.prevNext ) {
				that.prev = that.renderButton({
					class: o.classes.prev,
					content: o.prevText,
					page: that.currentPage > 1 ? that.currentPage - 1 : 1,
					nav: true,
					prev: true
				});

				node.appendChild(that.prev);
			}
		}

		each(items, function(item, i) {
			node.appendChild(item);
		});
		
		if ( that.hideDisabled && that.currentPage === that.totalPages ) {
		} else {
			if ( o.prevNext ) {
				that.next = that.renderButton({
					class: o.classes.next,
					content: o.nextText,
					page: that.currentPage < that.totalPages ? that.currentPage + 1 : that.totalPages,
					nav: true,
					next: true
				});

				node.appendChild(that.next);
			}

			if ( o.firstLast ) {
				that.last = that.renderButton({
					class: o.classes.last,
					content: o.lastText,
					page: that.totalPages,
					nav: true,
					last: true
				});

				node.appendChild(that.last);
			}	
		}	
		
		that.pager.innerHTML = "";
		that.pager.appendChild(node);

		that.container.appendChild(that.pager);

		that.emit("render");
	};
	
	Pager.prototype.renderButton = function(obj) {
		var that = this, o = that.config;

		var item = createNode("li", {
			class: o.classes.item
		});
		
		item.dataset.page = obj.page;
		
		if ( obj.page === that.currentPage && !obj.ellipsis && !obj.nav) {
			item.classList.add(o.classes.active);
		}

		var link = createNode(obj.ellipsis ? "span" : "a", {
			class: !obj.ellipsis ? o.classes.link : "",
			html: obj.content
		});
		
		if ( obj.class ) {
			item.classList.add(obj.class);
		}
		
		if ( obj.nav ) {
			item.nav = true;
		}
		
		if ( obj.ellipsis ) {
			item.ellipsis = true;
		} else {
			item.item = true;
			link.href = o.hashString.replace("{page}", obj.page).replace("{pages}", that.totalPages);
		}
		
		if ( (obj.prev || obj.first) && that.currentPage === 1 ||
			 	 (obj.next || obj.last) && that.currentPage === that.totalPages )	{
			item.disabled = true;
			item.classList.add(o.classes.disabled);
		
			link.tabIndex = -1;
		} else {
			item.disabled = false;
		}

		item.appendChild(link);
		
		return item;
	};
	
	Pager.prototype.goTo = function(page) {
		
		var that = this, o = that.config;
		
		if ( o.ajax ) {

			o.ajax.data = o.ajax.data || {}

			o.ajax.data[o.ajax.param || "page"] = page;

			// https://stackoverflow.com/questions/316781/how-to-build-query-string-with-javascript/34209399#34209399
			var esc = encodeURIComponent;
			var query = Object.keys(o.ajax.data)
					.map(k => esc(k) + '=' + esc(o.ajax.data[k]))
					.join('&');				

			var request = new Request(o.ajax.url + "?" + query, {
					method: "GET", 
					headers: new Headers()
			});
			
			if ( typeof o.ajax.before === "function" ) {
				o.ajax.before.call(that, data);
			}	

			fetch(request).then(function (response) { return response.json(); })
				.then(function (data) {
				
					that.currentPage = page;

					if ( typeof o.ajax.success === "function" ) {
						o.ajax.success.call(that, data);
					}

					that.render();

					that.emit("change", page);
				});
		} else {
			
			that.currentPage = page;
			that.render();

			that.emit("change", page);				
		}		
	};
	
	Pager.prototype.truncate = function() {

		var that = this;
		var page = that.currentPage;
		var pages = that.totalPages;
		var delta = that.offset;
		var offset = delta * 2;
		var left = page - delta;
		var right = page + delta;
		var range = [];
		var pager = [];
		var k;
		
		// No need to truncate if the number of pages is low
		if (!this.limit || this.totalPages <= this.limit) {
			each(pages, function(index) {
				pager.push(that.renderButton({
					page: index,
					content: index
				}));
			});
		} else {
			if ( page < (4 - delta) + offset ) {
				right = 3 + offset;
			} else if ( page > pages - ((3 - delta) + offset)  ) {
				left = pages - (2 + offset);
			}

			for (let i = 1; i <= pages; i++) {
				if (i == 1 || i == pages || i >= left && i <= right) {
					range.push(that.renderButton({
						page: i,
						content: i
					}));
				}
			}

			each(range, (link) => {
				var page = getPage(link);
				if (k) {
					var p = getPage(k);
					if (page - p == 2) {
						pager.push(that.renderButton({
							page: p + 1,
							content: p + 1
						}));
					} else if (page - p != 1) {
						pager.push(that.renderButton({
							class: that.config.classes.ellipsis,
							content: that.config.ellipsisText,
							ellipsis: true
						}));
					}
				}
				pager.push(link);
				k = link;
			});
		}

		return pager;
	};	
	
	Pager.prototype.add = function() {
		this.render(this.totalPages + 1);

		this.emit("add");
	};

	Pager.prototype.remove = function(num) {
		if (this.totalPages > 1) {
			this.render(this.totalPages - 1);
			
			this.emit("remove");
		}
	};	
	
	Pager.prototype.on = function(event, fct) {
		this.events[event] = this.events[event] || [];
		this.events[event].push(fct);
	};
	
	Pager.prototype.off = function(event, fct) {
		if (event in this.events === false) return;
		this.events[event].splice(this.events[event].indexOf(fct), 1);
	};
	
	Pager.prototype.emit = function(event /* , args... */) {
		if (event in this.events === false) return;
		for (var i = 0; i < this.events[event].length; i++) {
			this.events[event][i].apply(
				this,
				Array.prototype.slice.call(arguments, 1)
			);
		}
	};
	
	Pager.prototype.set = function(prop, value) {
		this[prop] = value;
	};	
	
	Pager.prototype.setLimit = function(limit) {
		this.limit = parseInt(limit, 5);
	};
	
	Pager.prototype.setOffset = function(offset) {
		this.offset = parseInt(offset, 5);
	};
	
	Pager.prototype.getLimit = function() {
		return this.limit;
	};
	
	Pager.prototype.getOffset = function() {
		return this.offset;
	};	

	root.Pager = Pager;
})(this);

const config = {
	container: "#pager",
	limit: 5,
	// startPage: 10,
	firstLast: true,
	hideDisabled: false,
	hashString: "?page={page}",
	prevText: '<span class="mdi mdi-chevron-left"></span>',
	nextText: '<span class="mdi mdi-chevron-right"></span>',
	firstText: '<span class="mdi mdi-chevron-double-left"></span>',
	lastText: '<span class="mdi mdi-chevron-double-right"></span>',	
	ellipsisText: '<span class="mdi mdi-dots-horizontal"></span>',	
};

const pager = new Pager(config)
pager.render(5);


/* DEMO STUFF */
const $ = el => document.getElementById(el);
const $$ = el => document.querySelectorAll(el);

const classes = pager.config.classes;
const limit = $("limit");
const offset = $("offset");
const pages = $("pages");
const page = $("page");
const info = $("info");
const trunc = $("truncation");
const truncs = $$(".truncation");
const hide = $("hideDisabled");
const hides = $$(".hide-disabled");
const skin = $("skin");
const skins = $$(".skin");

pager.on("init", init);

pager.on("render", update)

pager.on("change", update);

pager.on("add", update);

pager.on("remove", update);

skin.addEventListener("change", changeSkin, false);

hide.addEventListener("change", e => {
	var input = e.target;
	var val = parseInt(input.value, 5);

	pager.set("hideDisabled", val ? true : false);
	pager.render();

}, false);

trunc.addEventListener("change", e => {
	var input = e.target;
	var val = parseInt(input.value, 5);
	
	var shitTonsOfLinks = false;
	
	if ( !val && parseInt(pages.value, 5) >= 1000 ) {
		shitTonsOfLinks = !confirm("You have a shit-ton of pages!! Are you sure you want to disable truncation and render all the links?");
	}
	
	if ( !shitTonsOfLinks ) {
		pager.setLimit(val ? limit.value : val);
		pager.render();

		limit.disabled = !val;
		offset.disabled = !val;
	} else {
		truncs[0].checked = true;
	}
}, false);

pages.addEventListener("change", e => {
	var max = parseInt(pages.value, 5);
	var val = parseInt(page.value, 5);
	pager.render(max);
	page.max = max;
	
	if ( val > max ) {
		page.value = max
	}
}, false);

page.addEventListener("change", e => {
	pager.goTo(parseInt(page.value, 5));
}, false);

limit.addEventListener("change", e => {
	pager.setLimit(limit.value);
	pager.render();
}, false);

offset.addEventListener("change", e => {
	pager.setOffset(offset.value);
	pager.render();
}, false);

function init() {
	
	limit.disabled = !truncs[0].checked;
	offset.disabled = !truncs[0].checked;	
	
	skins[0].checked = true;
	hides[0].checked = true;
	truncs[0].checked = true;
	
	pages.value = 5;
	page.value = 1;
	page.max = 5;
	limit.value = 5;
	offset.value = 2;
	update();
}

function update() {
	page.value = pager.currentPage;
	info.textContent = `Page ${pager.currentPage} of ${pager.totalPages}`;
}

function changeSkin(e) {
	var val = e.target.value;
	
	if ( val === "bootstrap" ) {
		pager.config.prevText = "&lsaquo;";
		pager.config.nextText = "&rsaquo;";
		pager.config.firstText = "&laquo;";
		pager.config.lastText = "&raquo;";
		pager.config.ellipsisText = "&hellip;";
			
		pager.config.classes = {
			pager: "pagination",
			item: "page-item",
			link: "page-link",
			prev: "page-item",
			next: "page-item",
			first: "page-item",
			last: "page-item",		
			active: "active",		
			disabled: "disabled",
			ellipsis: "page-link",
		};
	} else {
		pager.config.classes = classes;
	pager.config.prevText = '<span class="mdi mdi-chevron-left"></span>';
	pager.config.nextText = '<span class="mdi mdi-chevron-right"></span>';
	pager.config.firstText = '<span class="mdi mdi-chevron-double-left"></span>';
	pager.config.lastText = '<span class="mdi mdi-chevron-double-right"></span>';
	pager.config.ellipsisText = '<span class="mdi mdi-dots-horizontal"></span>';
	}

	pager.render();
}