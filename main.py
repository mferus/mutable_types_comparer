# -*- coding: utf-8; -*-


class Comparer:
    def __init__(self, first_data, second_data):
        self.first = first_data
        self.second = second_data


class MutableTypesComparer:
    def __init__(self,
                 first_data,
                 second_data,
                 _name_tag="main dict",
                 check_length=True,
                 check_types=False,
                 debug=False,
                 grid="",
                 simplify_second_comparison=True
                 ):
        self.first_data = first_data
        self.second_data = second_data
        self.comparer = Comparer(self.first_data, self.second_data)
        self.name_tag = _name_tag
        self.simplify_second_comparison = simplify_second_comparison
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

    def compare(self):
        if self.name_tag == "main dict":
            print("Instance Type: {}".format(type(self.first_data).__name__))
        self._compare_data()
        self.comparer = Comparer(self.second_data, self.first_data)
        if self.simplify_second_comparison:
            self._compare_second_to_first()
        else:
            self._compare_data()
        self._print_results()
        return self.differences_amount, self.iteration_amount

    def _compare_data(self):
        for index, element in enumerate(self.comparer.first):
            is_different = False
            if self.is_dict:
                is_different = self._compare_dict(element)
            elif self.is_list:
                is_different = self._compare_list(element, index)
            elif self.is_set:
                is_different = self._compare_set(element)
            if is_different:
                self.differences_amount += 1
            self.iteration_amount += 1

    def _compare_second_to_first(self):
        for element in self.second_data:
            is_different = False
            if self.is_dict:
                if self._is_element_in_first_dict(element):
                    is_different = True
            elif self.is_set:
                is_different = self._compare_set(element)
            if is_different:
                self.differences_amount += 1
            self.iteration_amount += 1

    def _is_element_in_first_dict(self, element):
        is_different = False
        if element not in self.first_data:
            self.not_in.append(
                self.grid + 'element {:^64} not in first dict: {:^154}'.format(element, self.second_data[element]))
            is_different = True
        return is_different

    def _compare_dict(self, element, is_different=False):
        if self._is_element_in_dict(element):
            is_different = True
        else:
            if not self._proceed_if_modular(self.comparer.first[element], self.comparer.second[element], element):
                if not self._is_type_different(self.comparer.first[element], self.comparer.second[element], element):
                    if self.comparer.second[element] and \
                        type(self.comparer.first[element]) not in [bool, int, float, None] and \
                            self.is_length_different(self.comparer.first[element], self.comparer.second[element], element):
                        is_different = True
                    if self._is_different(self.comparer.first[element], self.comparer.second[element], element):
                        is_different = True
                else:
                    is_different = True
        return is_different

    def _compare_list(self, element, index, is_different=False):
        try:
            if self.is_length_different(self.comparer.first, self.comparer.second, element):
                is_different = True
            if not self._is_type_different(element, self.comparer.second[index], self.comparer.first[element]):
                if not self._proceed_if_modular(element, self.comparer.second[index], str(index)):
                    if type(element) not in [bool, int, float, None] and \
                            self.is_length_different(element, self.comparer.second[index], element):
                        is_different = True
                    if self._is_different(element, self.comparer.second[index], self.comparer.first[element]):
                        is_different = True
            else:
                is_different = True
        except IndexError:
            pass
        return is_different

    def _compare_set(self, element, is_different=False):
        if element not in self.comparer.second:
            self.not_equal.append(
                self.grid + 'element not in set: {:^154}'.format(element))
            is_different = True
        return is_different

    def _is_type_different(self, element_a, element_b, element_name):
        is_different = False
        if type(element_a) != type(element_b):
            self.not_equal.append(
                self.grid + 'element {:^64} type not same: {:^64} != {:^64}'.format(
                    element_name, type(element_a).__name__, type(element_b).__name__))
            is_different = True
        return is_different

    def _is_element_in_dict(self, element):
        is_different = False
        if element not in self.comparer.second:
            self.not_in.append(
                self.grid + 'element {:^64} not in dict: {:^158}'.format(element, self.comparer.first[element]))
            is_different = True
        return is_different

    def is_length_different(self, element_a, element_b, element_name):
        len_a = len(element_a)
        len_b = len(element_b)
        is_different = False
        if len_a != len_b and self.check_length:
            self.not_equal.append(self.grid + 'element {:^64} has not the same length: {:^70} != {:^64}'.format(
                element_name, len_a, len_b))
            is_different = True
        return is_different

    def _is_different(self, element_a, element_b, element_name):
        is_different = False
        if element_a != element_b:
            self.not_equal.append(self.grid + 'element {:^64} not same: {:^64} != {:^64}'.format(
                element_name, element_a, element_b))
            is_different = True
        else:
            self.equal.append(self.grid + 'element {:^64} same: {:^64} == {:^64}'.format(
                element_name, element_a, element_b))
        return is_different

    def _proceed_if_modular(self, element, second_element, name):
        proceeded = False
        if type(element) in [list, dict]:
            print(self.grid + "Comparing {} element '{}'...".format(type(element).__name__, name))
            name = "list" if type(element) == list else name
            differences_amount, iteration_amount = MutableTypesComparer(
                element,
                second_element,
                _name_tag=name,
                debug=self.debug,
                check_length=self.check_length,
                check_types=self.check_types,
                grid=self.grid + "    ",
                simplify_second_comparison=self.simplify_second_comparison
            ).compare()
            self.differences_amount += differences_amount
            self.iteration_amount += iteration_amount
            proceeded = True
        return proceeded

    def _print_results(self):
        if self.name_tag != "list":
            print(self.grid + '-' * 3)
            print(self.grid + "\'" + self.name_tag + "\' result:")
            if any([self.not_in, self.not_equal]) or self.differences_amount > 0:
                for element in self.not_in + self.not_equal:
                    print(element)
                print(self.grid + 'Differences amount: {}'.format(self.differences_amount))
            elif self.equal:
                print(self.grid + 'The content is the same')
            if self.debug:
                for element in self.equal:
                    print(element)
            print(self.grid + 'Iteration amount: {}'.format(self.iteration_amount))
            print(self.grid + '-' * 3)


if __name__ == '__main__':

    a = {}
    b = {}

    comparer = MutableTypesComparer(a, b, check_types=True)
    comparer.compare()