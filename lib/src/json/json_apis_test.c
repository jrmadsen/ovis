/*
 * json_apis_test.c
 *
 *  Created on: Apr 19, 2019
 *      Author: monn
 */

#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include "json_util.h"

/*
 * * entity new
 * * list: item_add
 * * dict: attr_add, attr_mod, attr_remove
 */

static int is_same_entity(json_entity_t l, json_entity_t r)
{
	int i;
	double d;
	json_entity_t a, b;

	if (l->type != r->type)
		return 0;

	switch (l->type) {
	case JSON_INT_VALUE:
		return (l->value.int_ == r->value.int_)?1:0;
	case JSON_BOOL_VALUE:
		return (l->value.bool_ == r->value.bool_)?1:0;
	case JSON_FLOAT_VALUE:
		return (l->value.double_ == r->value.double_)?1:0;
	case JSON_STRING_VALUE:
		return (0 == strcmp(l->value.str_->str, r->value.str_->str))?1:0;
	case JSON_ATTR_VALUE:
		if (0 != strcmp(json_attr_name(l)->str, json_attr_name(r)->str))
			return 0;
		else
			return is_same_entity(json_attr_value(l), json_attr_value(r));
	case JSON_LIST_VALUE:
		/* The order MUST be the same */
		a = json_item_first(l);
		b = json_item_first(r);
		while (a && b) {
			if (!is_same_entity(a, b))
				return 0;
			a = json_item_next(a);
			b = json_item_next(b);
		}
		/* In case the list lengths are different */
		if (a || b)
			return 0;
		break;
	case JSON_DICT_VALUE:
		a = json_attr_first(l);
		while (a) {
			b = json_attr_find(r, json_attr_name(a)->str);
			if (!b)
				return 0;
			if (!is_same_entity(a, b))
				return 0;
			a = json_attr_next(a);
		}
		/* Check the other way around in case that x has more attributes than e */
		b = json_attr_first(r);
		while (b) {
			a = json_attr_find(l, json_attr_name(b)->str);
			if (!a)
				return 0;
			/*
			 * No need to check if a == b.
			 * It was verified in the above loop.
			 */
			b = json_attr_next(b);
		}
		break;
	default:
		break;
	}
	return 1;
}

static void test_json_dict_apis()
{
	json_entity_t d, a, av, x, y, avl, avd, exp;
	int type;
	char *type_s;

	printf("---- TEST:  json dict APIs ------\n");

	d = json_entity_new(JSON_DICT_VALUE);
	assert(d);

	x = json_entity_new(JSON_STRING_VALUE, "a");
	y = json_entity_new(JSON_STRING_VALUE, "b");

	printf("----------  json_attr_add()  ------\n");
	/* json_attr_add */
	for (type = JSON_INT_VALUE; type < JSON_NULL_VALUE; type++) {
		switch (type) {
		case JSON_INT_VALUE:
		case JSON_BOOL_VALUE:
			av = json_entity_new(type, 1);
			break;
		case JSON_FLOAT_VALUE:
			av = json_entity_new(type, 1.0);
			break;
		case JSON_STRING_VALUE:
			av = json_entity_new(type, "1st");
			break;
		case JSON_ATTR_VALUE:
			av = json_entity_new(type, x, y);
			break;
		case JSON_LIST_VALUE:
			av = json_entity_new(type);
			break;
		case JSON_DICT_VALUE:
			av = json_entity_new(type);
			assert(NULL == json_attr_first(av));
			break;
		default:
			assert(0 == "unrecognized type");
		}
		exp = av;

		type_s = (char *)json_type_names[type];
		a = json_entity_new(JSON_ATTR_VALUE,
			json_entity_new(JSON_STRING_VALUE, type_s), av);
		/* Add the attribute */
		json_attr_add(d, a);

		/* verify */
		a = json_attr_find(d, type_s);
		av = json_attr_value(a);
		assert(is_same_entity(av, exp));
	}

	x = json_entity_new(JSON_STRING_VALUE, "aname_2");
	y = json_entity_new(JSON_STRING_VALUE, "avalue_2");
	/* json_attr_mod */
	printf("----------  json_attr_mod()  ------\n");
	for (type = JSON_INT_VALUE; type < JSON_NULL_VALUE; type++) {
		type_s = (char *)json_type_names[type];
		switch (type) {
		case JSON_INT_VALUE:
		case JSON_BOOL_VALUE:
			json_attr_mod(d, type_s, 2);
			a = json_attr_find(d, type_s);
			assert(is_same_entity(json_attr_value(a), json_entity_new(type, 2)));
			break;
		case JSON_FLOAT_VALUE:
			json_attr_mod(d, type_s, 2.2);
			a = json_attr_find(d, type_s);
			assert(is_same_entity(json_attr_value(a), json_entity_new(type, 2.2)));
			break;
		case JSON_STRING_VALUE:
			json_attr_mod(d, type_s, "2nd");
			a = json_attr_find(d, type_s);
			assert(is_same_entity(json_attr_value(a), json_entity_new(type, "2nd")));
			break;
		case JSON_ATTR_VALUE:
			av = json_entity_new(JSON_ATTR_VALUE, x, y);

			json_attr_mod(d, type_s, av);

			a = json_attr_find(d, type_s);
			assert(is_same_entity(json_attr_value(a), av));
			break;
		case JSON_LIST_VALUE:
			av = json_entity_new(JSON_LIST_VALUE);
			json_item_add(av, x);
			json_item_add(av, y);

			json_attr_mod(d, type_s, av);

			a = json_attr_find(d, type_s);
			assert(is_same_entity(json_attr_value(a), av));
			break;
		case JSON_DICT_VALUE:
			av = json_entity_new(JSON_DICT_VALUE);
			json_attr_add(av, json_entity_new(JSON_ATTR_VALUE,
				json_entity_new(JSON_STRING_VALUE, "attr1"), x));
			json_attr_add(av, json_entity_new(JSON_ATTR_VALUE,
				json_entity_new(JSON_STRING_VALUE, "attr2"), y));

			json_attr_mod(d, type_s, av);

			a = json_attr_find(d, type_s);
			assert(is_same_entity(json_attr_value(a), av));
			break;
		default:
			break;
		}
	}

	/* json_attr_rem */
	printf("----------  json_attr_rem()  ------\n");
	for (type = JSON_INT_VALUE; type < JSON_NULL_VALUE; type++) {
		type_s = (char *)json_type_names[type];
		json_attr_rem(d, type_s);
		av = json_attr_find(d, type_s);
		assert(av == NULL);
	}

	json_entity_free(d);

}

struct my_exp {
	enum json_value_e type;
	char *v;
};
static void test_json_entity_copy()
{
	printf("---- TEST: json_entity_copy()------\n");
	struct my_exp exp[] = {
		{ JSON_INT_VALUE,      "1"                   },
		{ JSON_BOOL_VALUE,     "true"                },
		{ JSON_FLOAT_VALUE,    "1.1"                 },
		{ JSON_STRING_VALUE,   "\"foo\"",                },
		{ JSON_LIST_VALUE,     "[ \"foo\", 1 ]"      },
		{ JSON_DICT_VALUE,     "{ \"name\": \"value\", \"name2\": \"value2\" }" },
		{ 0, NULL },
	};

	int rc, i;
	enum json_value_e type;
	json_entity_t e, dup;
	json_parser_t parser;

	for (i = 0; exp[i].v; i++) {
		printf("-------------- %s\n", json_type_names[exp[i].type]);
		parser = json_parser_new(0);
		assert(parser);
		rc = json_parse_buffer(parser, exp[i].v, strlen(exp[i].v), &e);
		assert(0 == rc);
		dup = json_entity_copy(e);
		assert(dup);
		assert(1 == is_same_entity(dup, e));
		json_entity_free(dup);
		json_entity_free(e);
		json_parser_free(parser);
	}
}

static void test_json_entity_dump(json_entity_t *jsons)
{
	int i;
	jbuf_t jb;

	printf("---- TEST: json_entity_dump()------\n");
	for (i = 0; i < JSON_NULL_VALUE; i++) {
		jb = json_entity_dump(NULL, jsons[i]);
		if (!jb)
			assert(0);
		printf("-------- %s: %s\n", json_type_names[i], jb->buf);
	}
}

#define LEN 3
static void test_apis() {
	json_entity_t jsons[JSON_NULL_VALUE];
	json_entity_t attr_name, attr_value, e;
	int type, i;

	printf("---- TEST: json_entity_new() ------ \n");
	for (type = JSON_INT_VALUE; type < JSON_NULL_VALUE; type++) {
		switch (type) {
		case JSON_INT_VALUE:
			e = json_entity_new(type, 1);
			assert(1 == e->value.int_);
			break;
		case JSON_BOOL_VALUE:
			e = json_entity_new(type, 1);
			assert(1 == e->value.bool_);
			break;
		case JSON_FLOAT_VALUE:
			e = json_entity_new(type, 1.0);
			assert(1.0 == e->value.double_);
			break;
		case JSON_STRING_VALUE:
			e = json_entity_new(type, "foo");
			assert(0 == strcmp("foo", e->value.str_->str));
			break;
		case JSON_ATTR_VALUE:
			attr_name = json_entity_new(JSON_STRING_VALUE, "name");
			attr_value = json_entity_new(JSON_STRING_VALUE, "value");
			e = json_entity_new(type, attr_name, attr_value);
			assert(0 == strcmp("name", json_attr_name(e)->str));
			assert(is_same_entity(attr_value, json_attr_value(e)));
			break;
		case JSON_LIST_VALUE:
			e = json_entity_new(type);
			assert(is_same_entity(e, json_entity_new(type)));
			break;
		case JSON_DICT_VALUE:
			e = json_entity_new(type);
			assert(is_same_entity(e, json_entity_new(type)));
			break;
		default:
			assert(0 == "unrecognized");
			break;
		}
		jsons[type] = e;
	}

	/* json dict APIs */
	test_json_dict_apis();

	test_json_entity_copy();

	test_json_entity_dump(jsons);
}

int main(int argc, char **argv) {
	printf("start\n");
	test_apis();
	printf("DONE\n");
}

