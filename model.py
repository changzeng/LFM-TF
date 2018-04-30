# encoding: utf-8

# author: liaochangzeng
# github: https://github.com/changzeng

import tensorflow as tf

class LFM(object):
    def __init__(self, user_num=1000, item_num=2000, batch_size=60, hidden_dim=10):
        self.user_num = user_num
        self.item_num = item_num
        self.batch_size = batch_size
        self.hidden_dim = hidden_dim
        self.build_graph()

    def build_graph(self):
        self.input = tf.placeholder(shape=[self.batch_size, 2], dtype=tf.int32, name="input")
        self.users = tf.reshape(tf.slice(self.input, [0, 0], [self.batch_size, 1]), [self.batch_size])
        self.items = tf.reshape(tf.slice(self.input, [0, 1], [self.batch_size, 1]), [self.batch_size])
        self.score = tf.placeholder(shape=[self.batch_size],dtype=tf.float32,  name="score")

        # user hidden matrix and item hidden matrix
        self.user_mat = tf.Variable(tf.random_normal([self.user_num, self.hidden_dim]), tf.float32)
        self.item_mat = tf.Variable(tf.random_normal([self.hidden_dim, self.item_num]), tf.float32)

        select_user_mat = []
        select_item_mat = []
        for i in range(self.batch_size):
            select_user_mat.append(tf.expand_dims(tf.reshape(tf.slice(self.user_mat, [self.users[i], 0], [1, self.hidden_dim]), [self.hidden_dim]), -1))
            select_item_mat.append(tf.expand_dims(tf.reshape(tf.slice(self.item_mat, [0, self.items[i]], [self.hidden_dim, 1]), [self.hidden_dim]), -1))

        select_user_mat = tf.matrix_transpose(tf.concat(select_user_mat, axis=1))
        select_item_mat = tf.concat(select_item_mat, axis=1)

        predict_mat = tf.matmul(select_user_mat, select_item_mat)
        predict = []
        for i in range(self.batch_size):
            predict.append(tf.slice(predict_mat, [i, i], [1, 1]))
        self.predict = tf.reshape(tf.concat(predict, 0), [self.batch_size])

        self.global_step = tf.Variable(0, dtype=tf.int32, name="global_sep", trainable=False)
        self.loss = tf.reduce_mean(tf.square(self.predict - self.score), name="loss") + tf.reduce_sum(tf.square(select_user_mat)) + tf.reduce_sum(tf.square(select_item_mat))
        tf.summary.scalar("loss", self.loss)
        self.optimizer = tf.train.AdamOptimizer(1e-3)
        self.train = self.optimizer.apply_gradients(self.optimizer.compute_gradients(self.loss), global_step=self.global_step)

        self.saver = tf.train.Saver(tf.global_variables())

    def save(self, sess, model_path, global_step):
        self.saver.save(sess, model_path, global_step=global_step)

    def restore(self, sess, model_path):
        self.saver.restore(sess, model_path)


if __name__ == "__main__":
    lfm = LFM()
