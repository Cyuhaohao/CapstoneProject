# This File is used to generate the random creature for the game.
# However, this is a bug concerning the version of tensorflow. I will fix it later.

import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import Model,optimizers
from tensorflow.keras.layers import Input, Dense, BatchNormalization, Reshape, Conv2DTranspose, Conv2D, LeakyReLU, Flatten, Dropout


# Define the loss function for the generator, the input is the probability of generated images are considered genuine
def loss_generator(prob):
    # Mean of log of prob of tensors
    return tf.math.negative(tf.math.reduce_mean(tf.math.log(prob)))

# Define the loss function for the discriminator
def loss_discriminator(p_real, p_fake):
    # The sub-loss to recognize real images as real
    loss_real = tf.math.negative(tf.math.reduce_mean(tf.math.log(p_real)))
    # The sub-loss to recognize fake images as fake
    loss_fake = tf.math.negative(tf.math.reduce_mean(tf.math.log(1 - p_fake)))
    # Total loss_function equals to the sum of two sub_loss
    return loss_real + loss_fake

# Define the CNN for Generator
def Generator(output_channels, noise_size):
    # Define the input with the noise
    X = Input(shape=noise_size)

    # Project the input noise to the size of 4x4
    Y = Dense(units=4*4*256)(X)
    # Add Leaky Relu for the activision of the network
    Y = LeakyReLU()(Y)
    # Add a batch normalization layer
    Y = BatchNormalization()(Y)
    # Reshape the input to 4*4*256
    Y = Reshape(target_shape=(4, 4, 256))(Y)

    # Amplify the input to 8x8
    # Use a deconvolution layer to transpose the convolution operation
    Y = Conv2DTranspose(filters=128, kernel_size=5, strides=2, padding='same', activation='relu')(Y)
    # Add a # Add a batch normalization layer
    Y = BatchNormalization()(Y)

    # Amplify the input to 16x16
    Y = Conv2DTranspose(filters=64, kernel_size=5, strides=2, padding='same', activation='relu')(Y)
    Y = BatchNormalization()(Y)

    # Amplify the input to 32x32
    Y = Conv2DTranspose(filters=32, kernel_size=5, strides=2, padding='same', activation='relu')(Y)
    Y = BatchNormalization()(Y)

    # Amplify the input to 64x64, use sigmoid as the activision function for the last layer
    Y = Conv2DTranspose(filters=output_channels, kernel_size=5, strides=2, padding='same', activation='sigmoid')(Y)

    # Construct the model
    model = Model(inputs=X, outputs=Y)

    return model

# Define a function to create the generator
def create_generator(channels, noise_size, learning_rate, beta_1):
    # Define the generator
    generator = Generator(output_channels=channels, noise_size=noise_size)
    # Use Adam as the optimizer of the training proccess, with a certain learning rate and hyperpara beta
    generator_optimizer = optimizers.Adam(lr=learning_rate, beta_1=beta_1)
    # Define the checkpoint to store model
    generator_checkpoint = tf.train.Checkpoint(optimizer=generator_optimizer, model=generator)

    return generator, generator_optimizer, generator_checkpoint

# Define the CNN for discriminator
def Discriminator(input_channels):
    # Define input arrays
    X = Input(shape=(64, 64, input_channels))

    # Project the input to 32x32
    # Add a convolutional layer
    Y = Conv2D(filters=32, kernel_size=5, strides=2, padding='same')(X)
    # Add Leaky Relu for the activision of the network
    Y = LeakyReLU()(Y)
    # Add a batch normalization layer
    Y = BatchNormalization()(Y)
    # Dropout 0.4 of tensors
    Y = Dropout(0.4)(Y)

    # Project the input to 16x16
    Y = Conv2D(filters=64, kernel_size=5, strides=2, padding='same')(Y)
    Y = LeakyReLU()(Y)
    Y = BatchNormalization()(Y)
    Y = Dropout(0.4)(Y)

    # Project the input to 8x8
    Y = Conv2D(filters=128, kernel_size=5, strides=2, padding='same')(Y)
    Y = LeakyReLU()(Y)
    Y = BatchNormalization()(Y)
    Y = Dropout(0.4)(Y)

    # Project the input to 4x4
    Y = Conv2D(filters=256, kernel_size=5, strides=2, padding='same')(Y)
    Y = LeakyReLU()(Y)
    Y = BatchNormalization()(Y)
    Y = Dropout(0.4)(Y)

    # Flatten the last layer to boolen and make the classification
    Y = Flatten()(Y)
    Y = Dense(units=1, activation='sigmoid')(Y)

    # Set the final model
    model = Model(inputs=X, outputs=Y)

    return model

# Define a function to create the generator
def create_discriminator(channels, learning_rate, beta_1):
    # Define the discriminator
    discriminator = Discriminator(input_channels=channels)
    # Use Adam as the optimizer of the training proccess, with a certain learning rate and hyperpara beta
    discriminator_optimizer = optimizers.Adam(lr=learning_rate, beta_1=beta_1)
    # Define the checkpoint to store model
    discriminator_checkpoint = tf.train.Checkpoint(optimizer=discriminator_optimizer, model=discriminator)

    return discriminator, discriminator_optimizer, discriminator_checkpoint

noise_size = 100
channels = 4
learning_rate = 0.0001
beta_1 = 0.5

# Create generators, optimizers, and checkpoints
generator, generator_optimizer, generator_checkpoint = create_generator(channels, noise_size, learning_rate, beta_1)
# Create discriminators, optimizers, and checkpoints
discriminator, discriminator_optimizer, discriminator_checkpoint = create_discriminator(channels, learning_rate, beta_1)

# Load the index of a checkpoint
checkpoint_dir="/game_resources/ckpt-43"
# from the DCGAN tutorial
checkpoint = tf.train.Checkpoint(
    generator_optimizer=generator_optimizer,
    discriminator_optimizer=discriminator_optimizer,
    generator=generator,
    discriminator=discriminator,
)

latest = tf.train.latest_checkpoint(checkpoint_dir)
checkpoint.restore(latest)

# generate an image
noise1 = tf.random.normal([100, noise_size])
prediction= checkpoint.generator(noise1)
print(prediction[0])
print(tf.__version__)
fig = plt.figure(figsize=(10, 10))

for i in range(1):
    plt.subplot(1, 1, i + 1)
    plt.imshow(prediction[i])
    plt.axis('off')

plt.show()

def create_creature():
    plt.savefig('animal.png')
