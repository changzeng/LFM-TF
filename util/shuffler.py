# encoding: utf-8

import os
import argparse
from random import randint, shuffle
from buffer_writer import BufferWriter

class Shuffler:
	def __init__(self, tmp_size=5000, buffer_file_num=10):
		self.tmp_size = tmp_size
		self.buffer_file_num = buffer_file_num

	def read_file(self, fd, num):
		result = []
		for i in range(num):
			a = fd.readline()
			b = fd.readline()
			c = fd.readline().strip()
			if len(a) == 0 or len(b) == 0:
				break
			d = fd.readline()
			result.append(a+b+c)
		return result

	def tmp_file_name(self, file_name, index):
		return file_name+".tmp_%d" % index

	def shuffle(self, file_name):
		self.shuffle_mul_file([file_name], file_name)

	def shuffle_mul_file(self, file_name_list, output_file_name):
		# create buffer writer
		tmp_writter = []
		for i in range(self.buffer_file_num):
			tmp_writter.append(BufferWriter(self.tmp_file_name(output_file_name, i), max_buffer_size=50*1024*1024, sep="\n\n"))

		for file_name in file_name_list:
			with open(file_name, "r", encoding="utf-8", errors="ignore") as fd:
				while True:
					tmp_list = self.read_file(fd, self.tmp_size)
					for item in tmp_list:
						index = randint(0, self.buffer_file_num-1)
						tmp_writter[index].update(item)
					if len(tmp_list) != self.tmp_size:
						break

		# close buffer writter
		for i in range(self.buffer_file_num):
			tmp_writter[i].close()

		order = list(range(0, self.buffer_file_num))
		shuffle(order)
		result_writter = BufferWriter(output_file_name, max_buffer_size=100*1024*1024, sep="\n\n")
		for index in order:
			tmp_file_name = self.tmp_file_name(output_file_name, index)
			with open(tmp_file_name, "r", encoding="utf-8", errors="ignore") as fd:
				while True:
					items = self.read_file(fd, self.tmp_size)
					if len(items) == 0:
						break
					result_writter.update_list(items)
					if len(items) != self.tmp_size:
						break
			# delete tmporary file
			os.remove(tmp_file_name)
		result_writter.close()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='bieshe artwork.')
	parser.add_argument('--file_name', type=str, default="test.txt", help='specify file name')
	args = parser.parse_args()

	shuffler = Shuffler()
	shuffler.shuffle(args.file_name)