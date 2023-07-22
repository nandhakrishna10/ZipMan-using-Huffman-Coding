from flask import Flask, request, render_template, jsonify

app = Flask(__name__, static_url_path='/static')


class MinHeap:
    def __init__(self):
        self.heap_array = []

    def push(self, element):
        self.heap_array.append(element)
        self._sift_up(len(self.heap_array) - 1)

    def pop(self):
        if self.size() == 0:
            return None
        self._swap(0, len(self.heap_array) - 1)
        min_element = self.heap_array.pop()
        self._sift_down(0)
        return min_element

    def top(self):
        if self.size() == 0:
            return None
        return self.heap_array[0]

    def size(self):
        return len(self.heap_array)

    def _swap(self, i, j):
        self.heap_array[i], self.heap_array[j] = self.heap_array[j], self.heap_array[i]

    def _sift_up(self, index):
        parent_index = (index - 1) // 2
        while index > 0 and self.heap_array[index][0] < self.heap_array[parent_index][0]:
            self._swap(index, parent_index)
            index = parent_index
            parent_index = (index - 1) // 2

    def _sift_down(self, index):
        left_child_index = 2 * index + 1
        right_child_index = 2 * index + 2
        smallest = index
        if (
                left_child_index < len(self.heap_array)
                and self.heap_array[left_child_index][0] < self.heap_array[smallest][0]
        ):
            smallest = left_child_index
        if (
                right_child_index < len(self.heap_array)
                and self.heap_array[right_child_index][0] < self.heap_array[smallest][0]
        ):
            smallest = right_child_index
        if smallest != index:
            self._swap(index, smallest)
            self._sift_down(smallest)


class Codec:
    def __init__(self):
        self.index = 0

    def getCodes(self, node, curr_code):
        if type(node[1]) == str:
            self.codes[node[1]] = curr_code
            return
        self.getCodes(node[1][0], curr_code + "0")
        self.getCodes(node[1][1], curr_code + "1")

    def make_string(self, node):
        if type(node[1]) == str:
            return "'" + node[1]
        return '0' + self.make_string(node[1][0]) + '1' + self.make_string(node[1][1])

    def make_tree(self, tree_string):
        node = []
        if tree_string[self.index] == "'":
            self.index += 1
            node.append(tree_string[self.index])
            self.index += 1
            return node
        elif tree_string[self.index] == '0':
            self.index += 1
            node.append(self.make_tree(tree_string))
            self.index += 1
            node.append(self.make_tree(tree_string))
            return node
        else:
            self.index += 1
            return self.make_tree(tree_string)

    def encode(self, data):
        self.heap = MinHeap()

        mp = {}
        for i in range(len(data)):
            if data[i] in mp:
                foo = mp[data[i]]
                mp[data[i]] = foo + 1
            else:
                mp[data[i]] = 1
        if len(mp) == 0:
            final_string = "zer#"
            output_message = "Compression complete and file sent for download. " + '\n' + "Compression Ratio : " + (
                    len(data) / len(final_string)).toPrecision(6)
            return [final_string, output_message]

        if len(mp) == 1:
            key, value = None, None
            for k, v in mp.items():
                key = k
                value = v
            final_string = "one" + '#' + key + '#' + str(value)
            output_message = "Compression complete and file sent for download. " + '\n' + "Compression Ratio : " + (
                    len(data) / len(final_string)).toPrecision(6)
            return [final_string, output_message]

        for key, value in mp.items():
            self.heap.push([value, key])

        while self.heap.size() >= 2:
            min_node1 = self.heap.top()
            self.heap.pop()
            min_node2 = self.heap.top()
            self.heap.pop()
            self.heap.push([min_node1[0] + min_node2[0], [min_node1, min_node2]])
        huffman_tree = self.heap.top()
        self.heap.pop()
        self.codes = {}
        self.getCodes(huffman_tree, "")

        binary_string = ""
        for i in range(len(data)):
            binary_string += self.codes[data[i]]
        padding_length = (8 - (len(binary_string) % 8)) % 8
        for i in range(padding_length):
            binary_string += '0'
        encoded_data = ""
        i = 0
        while i < len(binary_string):
            curr_num = 0
            for j in range(8):
                curr_num *= 2
                curr_num += int(binary_string[i]) - int('0')
                i += 1
            encoded_data += chr(curr_num)
        tree_string = self.make_string(huffman_tree)
        ts_length = len(tree_string)
        final_string = str(ts_length) + '#' + str(padding_length) + '#' + tree_string + encoded_data
        output_message = "Compression complete and file sent for download.\nCompression Ratio: {:.6f}".format(
            len(data) / len(final_string))
        return [final_string, output_message]

    def decode(self, data):  # Add 'self' parameter here
        k = 0
        temp = ""
        while k < len(data) and data[k] != '#':
            temp += data[k]
            k += 1
        if k == len(data):
            print("Invalid File!\nPlease submit a valid compressed .txt file to decompress and try again!")
            return
        if temp == "zer":
            decoded_data = ""
            output_message = "Decompression complete and file sent for download."
            return [decoded_data, output_message]
        if temp == "one":
            data = data[k + 1:]
            k = 0
            temp = ""
            while data[k] != '#':
                temp += data[k]
                k += 1
            one_char = temp
            data = data[k + 1:]
            str_len = int(data)
            decoded_data = ""
            for i in range(str_len):
                decoded_data += one_char
            output_message = "Decompression complete and file sent for download."
            return [decoded_data, output_message]
        data = data[k + 1:]
        ts_length = int(temp)
        k = 0
        temp = ""
        while data[k] != '#':
            temp += data[k]
            k += 1
        data = data[k + 1:]
        padding_length = int(temp)
        temp = ""
        for k in range(ts_length):
            temp += data[k]
        data = data[k:]
        tree_string = temp
        temp = ""
        for k in range(len(data)):
            temp += data[k]
        encoded_data = temp
        index = 0
        huffman_tree = self.make_tree(tree_string)

        binary_string = ""

        for i in range(len(encoded_data)):
            curr_num = ord(encoded_data[i])
            curr_binary = ""
            for j in range(7, -1, -1):
                foo = curr_num >> j
                curr_binary = curr_binary + str(foo & 1)
            binary_string += curr_binary

        binary_string = binary_string[:-padding_length]

        decoded_data = ""
        node = huffman_tree
        for i in range(len(binary_string)):
            if binary_string[i] == '1':
                node = node[1]
            else:
                node = node[0]

            if isinstance(node[0], str):
                decoded_data += node[0]
                node = huffman_tree
        output_message = "Decompression complete and file sent for download."
        return [decoded_data, output_message]


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/why')
def why():
    return render_template('why.html')

@app.route('/image')
def image():
    return render_template('image.html')

@app.route('/pdf')
def pdf():
    return render_template('pdf.html')

@app.route('/compress', methods=['POST'])
def compress():
    files = request.files.getlist('files[]')
    merged_data = ""

    for file in files:
        data = file.read().decode('utf-8')
        merged_data += data + '\n'

    codec = Codec()
    result = codec.encode(merged_data)

    return jsonify({'result': result})


@app.route('/decompress', methods=['POST'])
def decompress():
    files = request.files.getlist('files[]')
    merged_data = ""

    for file in files:
        data = file.read().decode('utf-8')
        merged_data += data + '\n'

    codec = Codec()
    result = codec.decode(merged_data)

    return jsonify({'result': result})


if __name__ == '__main__':
    app.run(debug=True)


""" Problem statement:- Develop an online application for a File Zipper project. For encoding, 
compress the input file passed using Huffman encoding. For decoding, the Huffman coded 
file is passed back to its original file. Also check the condition if the file exceeds 
a maximum size with alert boxes. If more than one input file, then merge the 
contents to a single file and then perform compression. """