import tensorflow as tf
with tf.device('/cpu:2'):
    import os
    import numpy as np
    import sys
    import skvideo.io
    import datetime
    from random import randint

    import keras
    from keras.layers import Input
    from load_dataset import read_dataset,input2data
    from DeepWarp import create_model, get_config
    from loopImages import ex_dim,images2mp4

    date_string = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path_random = str(randint(0,10000)).zfill(4)

    # img_path = 'bg3.jpg'
    IMAGE_PATH_ARGUMENT = 'image_path='
    ARG1 = sys.argv[1]
    img_path = ARG1[ARG1.find(IMAGE_PATH_ARGUMENT)+len(IMAGE_PATH_ARGUMENT):]
    app_root = os.path.dirname(os.path.dirname(img_path))
    dataImage_path = os.path.join(app_root, 'pyoutput/')
    userImage_path = os.path.join(dataImage_path, date_string+'_'+path_random+'/')
    if not os.path.isdir(dataImage_path):
        os.mkdir(dataImage_path)
    os.mkdir(userImage_path)

    '''setting input dimension'''
    is_cfw_only = True
    model_type = 'cfw_lcm'
    root_path = "E:/xampp/htdocs/gaze_manipulate"
    dataset = "test"
    if (is_cfw_only):
        model_type = 'cfw'
    conf = get_config()
    keras.backend.set_learning_phase(1)

    '''inputes'''
    input_ef = Input(shape=(conf.height, conf.width, conf.ef_dim), name = 'Input_ef', dtype = tf.float32)
    input_agl = Input(shape=(conf.agl_dim,), name = 'Input_agl', dtype = tf.float32)
    input_img = Input(shape=(conf.height, conf.width, conf.channel), name = 'Input_img', dtype = tf.float32)

    '''create network'''
    with tf.device('/gpu:1'):
        model_L = create_model(input_img, input_agl, input_ef, conf, cfw_only = is_cfw_only)
        model_L.load_weights(root_path + '/weights/bast_cfw_columbia_v4_L.h5')

        model_R = create_model(input_img, input_agl, input_ef, conf, cfw_only = is_cfw_only)
        model_R.load_weights(root_path + '/weights/bast_cfw_columbia_v4_R.h5')

    R_Xcen, R_Ycen, R_width, R_height, L_Xcen, L_Ycen, L_width, L_height, R_img, L_img, R_feature_point_layer, L_feature_point_layer = input2data(
        root_path+"/sp_full_ver.dat", img_path)

    decoded_imgs_L = []
    decoded_imgs_R = []

    img_r = np.uint8(R_img * 255)
    savenameR = os.path.join(userImage_path, 'test_R.png')
    skvideo.io.vwrite(savenameR, img_r)
    img_l = np.uint8(L_img * 255)
    savenameL = os.path.join(userImage_path, 'test_L.png')
    skvideo.io.vwrite(savenameL, img_l)

    # direction = 'shift'
    DIRECTION_ARGUMENT = 'direction='
    ARG2 = sys.argv[2]
    direction = ARG2[ARG2.find(DIRECTION_ARGUMENT)+len(DIRECTION_ARGUMENT):]

    if direction.startswith('sc') or direction.startswith('SC') or direction.startswith('Sc') :
        for i in range(15):
            x_train_R = ex_dim(R_img)
            x_train_L = ex_dim(L_img)
            feature_point_R = ex_dim(R_feature_point_layer)
            feature_point_L = ex_dim(L_feature_point_layer)
            angle_dif = np.array([[12 * i - 90, 0]])

            with tf.device('/gpu:1'):
                de_img_r = model_R.predict([feature_point_R, angle_dif, x_train_R])
                decoded_imgs_R.append(de_img_r)
                de_img_l = model_L.predict([feature_point_L, angle_dif, x_train_L])
                decoded_imgs_L.append(de_img_l)

            # de_img_r = model.predict([feature_point_R / 1.0, angle_dif / 1.0, x_train_R / 1.0])
            # decoded_imgs_R.append(de_img_r)
            # de_img_l = model.predict([feature_point_L / 1.0, angle_dif / 1.0, x_train_L / 1.0])
            # decoded_imgs_L.append(de_img_l)

    elif direction.startswith('sh') or direction.startswith('SH') or direction.startswith('Sh') :
        for i in range(15):
            x_train_R = ex_dim(R_img)
            x_train_L = ex_dim(L_img)
            feature_point_R = ex_dim(R_feature_point_layer)
            feature_point_L = ex_dim(L_feature_point_layer)
            angle_dif = np.array([[0, 12 * i - 90]])

            with tf.device('/gpu:1'):
                de_img_r = model_R.predict([feature_point_R, angle_dif, x_train_R])
                decoded_imgs_R.append(de_img_r)
                de_img_l = model_L.predict([feature_point_L, angle_dif, x_train_L])
                decoded_imgs_L.append(de_img_l)

            # de_img_r = model_R.predict([feature_point_R / 1.0, angle_dif / 1.0, x_train_R / 1.0])
            # decoded_imgs_R.append(de_img_r)
            # de_img_l = model_L.predict([feature_point_L / 1.0, angle_dif / 1.0, x_train_L / 1.0])
            # decoded_imgs_L.append(de_img_l)

    elif direction.startswith('mo') or direction.startswith('MO') or direction.startswith('Mo') :
        print("not done yet")
        exit()

    for count, img_r in enumerate(decoded_imgs_R, 1):
        img_r = np.uint8(img_r[0] * 255)
        imgname = 'eyeR_' + str(count).zfill(2) + '.png'
        savename = os.path.join(userImage_path,imgname)
        skvideo.io.vwrite(savename, img_r)
    for count, img_l in enumerate(decoded_imgs_L, 1):
        img_l = np.uint8(img_l[0] * 255)
        imgname = 'eyeL_' + str(count).zfill(2) + '.png'
        savename = os.path.join(userImage_path, imgname)
        skvideo.io.vwrite(savename, img_l)

    print(images2mp4(userImage_path,img_path,R_Xcen,R_Ycen,R_width,R_height,L_Xcen,L_Ycen,L_width,L_height))


