# -*- coding: utf-8; -*-


class Comparer:
    def __init__(self, first_data, second_data):
        self.first = first_data
        self.second = second_data

    def swap(self):
        self.first, self.second = self.second, self.first


class MutableTypesComparer:
    _name_tag = 'complete'

    def __init__(
        self,
        first_data,
        second_data,
        check_length=False,
        check_types=True,
        debug=False,
        grid="",
        simplify_second_comparison=True,
        avoid_logging_same_content=True,
    ):
        self.comparer = Comparer(first_data, second_data)
        self.simplify_second_comparison = simplify_second_comparison
        self.avoid_logging_same_content = avoid_logging_same_content
        self.debug = debug
        self.is_dict = isinstance(first_data, dict)
        self.is_list = isinstance(first_data, list)
        self.is_set = isinstance(first_data, set)
        self.differences_amount = 0
        self.iteration_amount = 0
        self.check_length = check_length
        self.check_types = check_types
        self.grid = grid
        self.not_in = []
        self.not_equal = []
        self.equal = []

    def compare(self) -> (int, int):
        if (
            self.avoid_logging_same_content
            and self.comparer.first == self.comparer.second
        ):
            print(self.grid + "Content of {} is identical".format(self._name_tag))
            self.iteration_amount += 1
        else:
            if isinstance(self.comparer.first, type(self.comparer.second)):
                if self._name_tag == comparer.__class__._name_tag:
                    print(
                        "Instance Types: {}".format(type(self.comparer.first).__name__)
                    )

                if self.comparer.second and not self.comparer.first:
                    print(
                        self.grid + "Content of first {} is empty".format(self._name_tag)
                    )
                    self.differences_amount += 1
                    self.iteration_amount += 1
                elif self.comparer.first and not self.comparer.second:
                    print(
                        self.grid
                        + "Content of second {} is empty".format(self._name_tag)
                    )
                    self.differences_amount += 1
                    self.iteration_amount += 1
                else:
                    self._compare_data()

                    self.comparer.swap()
                    if self.simplify_second_comparison:
                        self._simply_compare_data()
                    else:
                        self._compare_data()
                self._print_results()
            else:
                print(self.grid + "Given data is inconsistent")
                print(self.grid + f"First: {self.get_type_string(self.comparer.first)}")
                print(self.grid + f"Second: {self.get_type_string(self.comparer.second)}")
        return self.differences_amount, self.iteration_amount

    @staticmethod
    def get_type_string(element):
        return f"{type(element).__name__} - {element}"

    def _compare_data(self):
        for index, element in enumerate(self.comparer.first):
            is_different = False

            if self.is_dict:
                is_different = self._compare_dict(element)
            elif self.is_list:
                is_different = self._compare_list(index)
            elif self.is_set:
                is_different = self._compare_set(element)
            if is_different:
                self.differences_amount += 1
            self.iteration_amount += 1

    def _simply_compare_data(self):
        for element in self.comparer.first:
            is_different = False
            if self.is_dict:
                if self._is_element_in_first_dict(element):
                    is_different = True
            if is_different:
                self.differences_amount += 1
            self.iteration_amount += 1

    def _is_element_in_first_dict(self, element) -> bool:
        is_different = False
        if element not in self.comparer.second:
            self.not_in.append(
                self._get_print_message(
                    element, "not in first dict", repr(self.comparer.first[element])
                )
            )
            is_different = True
        return is_different

    def _get_print_message(self, *args) -> str:
        if len(args) == 2:
            template = "element {:^64} {:^156}"
        elif len(args) == 3:
            template = "element {:^64} {:^23} {:^132}"
        elif len(args) == 5:
            template = "element {:^64} {:^23} {:^64} {} {:^64}"
        else:
            raise RuntimeError(
                "Amount of arguments ({}) is inadequate.".format(len(args))
            )
        args = [str(arg) for arg in args]
        return self.grid + template.format(*args)

    def _compare_dict(self, element, is_different=False) -> bool:
        if self._is_element_in_dict(element):
            is_different = True
        else:
            if not self._proceed_if_mutable(
                self.comparer.first[element], self.comparer.second[element], element
            ):
                if not self._is_type_different(
                    self.comparer.first[element], self.comparer.second[element], element
                ):
                    if (
                        self.comparer.second[element]
                        and type(self.comparer.first[element])
                        not in [bool, int, float, None]
                        and self.is_length_different(
                            self.comparer.first[element],
                            self.comparer.second[element],
                            element,
                        )
                    ):
                        is_different = True
                    if self._is_different(
                        self.comparer.first[element],
                        self.comparer.second[element],
                        element,
                    ):
                        is_different = True
                else:
                    is_different = True
        return is_different

    def _compare_list(self, index: int, is_different=False) -> bool:
        try:
            if self.is_length_different(
                self.comparer.first, self.comparer.second, str(index)
            ):
                is_different = True
            if not self._proceed_if_mutable(
                self.comparer.first[index], self.comparer.second[index], str(index)
            ):
                if type(self.comparer.first[index]) not in [
                    bool, int, float, None,
                ] and self.is_length_different(
                    self.comparer.first[index], self.comparer.second[index], str(index)
                ):
                    is_different = True
                if self._is_element_in_list(
                    self.comparer.first[index], self.comparer.second
                ):
                    is_different = True
                if not self._is_type_different(
                    self.comparer.first[index], self.comparer.second[index], str(index)
                ):
                    is_different = True
                if self._is_different(
                    self.comparer.first[index], self.comparer.second[index], str(index)
                ):
                    is_different = True
        except IndexError:
            pass
        return is_different

    def _compare_set(self, element, is_different=False) -> bool:
        if element not in self.comparer.second:
            self.not_equal.append(self._get_print_message("not in second set", repr(element)))
            is_different = True
        return is_different

    def _is_type_different(self, element_a, element_b, element_name: str) -> bool:
        is_different = False
        if type(element_a) != type(element_b):
            self.not_equal.append(
                self._get_print_message(
                    element_name,
                    "type not same",
                    type(element_a).__name__,
                    "!=",
                    type(element_b).__name__,
                )
            )
            is_different = True
        return is_different

    def _is_element_in_dict(self, element) -> bool:
        is_different = False
        if element not in self.comparer.second:
            self.not_in.append(
                self._get_print_message(
                    element, "not in second dict", repr(self.comparer.first[element])
                )
            )
            is_different = True
        return is_different

    def _is_element_in_list(self, element, index: str) -> bool:
        is_different = False
        if element not in self.comparer.second:
            self.not_in.append(self._get_print_message(element, "not in second list", index))
            is_different = True
        return is_different

    def is_length_different(self, element_a, element_b, element_name: str) -> bool:
        len_a = len(element_a)
        len_b = len(element_b)
        is_different = False
        if len_a != len_b and self.check_length:
            self.not_equal.append(
                self._get_print_message(
                    element_name,
                    "has not the same length",
                    repr(len_a),
                    "!=",
                    repr(len_b),
                )
            )
            is_different = True
        return is_different

    def _is_different(self, element_a, element_b, element_name: str) -> bool:
        is_different = False
        if element_a != element_b:
            self.not_equal.append(
                self._get_print_message(
                    element_name, "not the same", repr(element_a), "!=", repr(element_b)
                )
            )
            is_different = True
        else:
            self.equal.append(
                self._get_print_message(
                    element_name, "same", repr(element_a), "==", repr(element_b)
                )
            )
        return is_different

    def _proceed_if_mutable(self, element, second_element, name: str) -> bool:
        proceeded = False
        if type(element) in [list, dict]:
            parent_type = type(self.comparer.first).__name__
            if parent_type == "list":
                name = "index {}".format(name)
            else:
                name = "key: '{}'".format(name)
            print(
                self.grid
                + "Comparing {} element which is {}. Comparing {}...".format(
                    parent_type, type(element).__name__, name
                )
            )
            name = "list" if type(element) == list else name
            recursive_comparer = MutableTypesComparer(
                element,
                second_element,
                debug=self.debug,
                check_length=self.check_length,
                check_types=self.check_types,
                grid=self.grid + "    ",
                simplify_second_comparison=self.simplify_second_comparison,
                avoid_logging_same_content=self.avoid_logging_same_content,
            )
            recursive_comparer._name_tag = name
            differences_amount, iteration_amount = recursive_comparer.compare()

            self.differences_amount += differences_amount
            self.iteration_amount += iteration_amount
            proceeded = True
        return proceeded

    def _print_results(self):
        print(self.grid + "-" * 3)
        print(self.grid + self._name_tag + " result:")
        if any([self.not_in, self.not_equal]) or self.differences_amount > 0:
            for element in self.not_in + self.not_equal:
                print(element)
            print(self.grid + "Differences amount: {}".format(self.differences_amount))
        elif self.equal:
            print(self.grid + "Content is identical")
        if self.debug:
            for element in self.equal:
                print(element)
        print(self.grid + "Iteration amount: {}".format(self.iteration_amount))
        print(self.grid + "-" * 3)


if __name__ == "__main__":

    a = {}
    b = {}

    comparer = MutableTypesComparer(a, b)
    comparer.compare()
