# encoding: utf-8

# author: liaochangzeng
# github: https://github.com/changzeng

import os
import time
import argparse
import numpy as np
import tensorflow as tf
from model import LFM
from random import shuffle


def get_div(a, b):
    if b == 0:
        return 0.0
    return a * 1.0 / b

def shuffle_file(file_name):
    with open(file_name, encoding="utf-8") as fd:
        txt = fd.read().strip()
        shuffle_result = txt.split("\n")
        shuffle(shuffle_result)
    with open(file_name, "w", encoding="utf-8") as fd:
        fd.write("\n".join(shuffle_result))


class Trainer(object):
    def __init__(self, args):
        self.model_time = int(time.time()) if args.model_time == None else args.model_time
        self.model_path = "model/" + str(self.model_time) + "/"
        self.checkpoint_path = self.model_path + "checkpoint/"
        self.summary_path = self.model_path + "summary/"
        self.max_epoch = args.max_epoch
        self.train_data = args.train_data
        self.test_data = args.test_data
        self.user_num = args.user_num
        self.item_num = args.item_num
        self.batch_size = args.batch_size
        self.hidden_dim = args.hidden_dim
        self.validate_epoch = args.validate_epoch
        self.checkpoint_epoch = args.checkpoint_epoch
        self.lfm = LFM(user_num=args.user_num, item_num=args.item_num, batch_size=args.batch_size, hidden_dim=args.hidden_dim)
        self.check_model_path()

    def check_model_path(self):
        for _path in ["model/", self.model_path, self.checkpoint_path, self.summary_path]:
            if not os.path.exists(_path):
                os.mkdir(_path)

    def train(self):
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            file_writer = tf.summary.FileWriter(self.summary_path, sess.graph)
            merged = tf.summary.merge_all()
            for epoch in range(self.max_epoch):
                for feed_dict in self.gen_batch(self.train_data):
                    _, global_step, summary = sess.run([self.lfm.train, self.lfm.global_step, merged], feed_dict=feed_dict)
                    if global_step % self.validate_epoch == 0:
                        self.validate(sess)
                    if global_step % self.checkpoint_epoch == 0:
                        self.lfm.save(sess, self.checkpoint_path+"model_{}.ckpt".format(int(time.time())), global_step)
                    file_writer.add_summary(summary, global_step)
                    print("cur_epoch/total_epoch: ({:3d}/{:3d}), global_step: {:4d}".format(epoch+1, self.max_epoch, global_step))

    def gen_batch(self, file_name):
        shuffle_file(file_name)
        with open(file_name, encoding="utf-8") as fd:
            while True:
                input_list = []
                score_list = []
                for i in range(self.batch_size):
                    line = fd.readline().strip()
                    if len(line) == 0:
                        return
                    _user, _item, _score, _ = line.split(",")
                    input_list.append([int(_user)-1, int(_item)-1])
                    score_list.append(_score)
                yield {"input:0": np.array(input_list, dtype=np.int32), "score:0": np.array(score_list, dtype=np.float32)}

    def validate(self, sess):
        total_loss = 0
        batch_num = 0
        for feed_dict in self.gen_batch(self.test_data):
            loss = sess.run(self.lfm.loss, feed_dict=feed_dict)
            total_loss += loss
            batch_num += 1
        print("Total loss is: {:4.2f}, Batch num is: {:4.2f}, Average loss is {:4.2f}".format(total_loss, batch_num, get_div(total_loss, batch_num)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LFM Model Training')
    parser.add_argument('--train_data', type=str, default="data/data.train", help='training data')
    parser.add_argument('--test_data', type=str, default="data/data.test", help='testing data')
    parser.add_argument('--user_num', type=int, default=6040, help='user num')
    parser.add_argument('--item_num', type=int, default=3952, help='item num')
    parser.add_argument('--batch_size', type=int, default=500, help='batch size')
    parser.add_argument('--hidden_dim', type=int, default=20, help='hidden dim')
    parser.add_argument('--max_epoch', type=int, default=20, help='opoch num')
    parser.add_argument('--validate_epoch', type=int, default=100, help='validate opoch num')
    parser.add_argument('--checkpoint_epoch', type=int, default=200, help='checkpoint opoch num')
    parser.add_argument('--model_time', type=str, default=None, help='time when training new model')
    args = parser.parse_args()

    trainer = Trainer(args)
    trainer.train()
