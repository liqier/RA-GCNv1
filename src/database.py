import os
import torch
import numpy as np
from torch.utils.data import Dataset


class NTU(Dataset):
    def __init__(self, path, type='train', setting='cs', data_shape=(3,300,25,2), transform=None):

        self.path = path
        self.maxC, self.maxT, self.maxV, self.maxM = data_shape
        self.transform = transform

        if not os.path.exists('./datasets/' + setting + '_' + type + '.txt'):
            self.get_train_list()

        fr = open('./datasets/' + setting + '_' + type + '.txt', 'r')
        self.files = fr.readlines()
        fr.close()

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        file_name = self.files[idx].strip()
        label = int(file_name.split('A')[1]) - 1

        data = np.zeros((self.maxC, self.maxT, self.maxV, self.maxM))
        location = np.zeros((2, self.maxT, self.maxV, self.maxM))
        with open(self.path + file_name, 'r') as fr:
            frame_num = int(fr.readline())
            for frame in range(frame_num):
                if frame >= self.maxT:
                    break
                person_num = int(fr.readline())
                for person in range(person_num):
                    fr.readline()
                    joint_num = int(fr.readline())
                    for joint in range(joint_num):
                        v = fr.readline().split(' ')
                        if joint < self.maxV and person < self.maxM:
                            data[0,frame,joint,person] = float(v[0])
                            data[1,frame,joint,person] = float(v[1])
                            data[2,frame,joint,person] = float(v[2])
                            location[0,frame,joint,person] = float(v[5])
                            location[1,frame,joint,person] = float(v[6])

        if self.transform:
            data = self.transform(data)

        data = torch.from_numpy(data).float()
        location = torch.from_numpy(location).float()
        label = torch.from_numpy(np.array(label)).long()
        return data, location, label, file_name

    def get_train_list(self):
        folder = '/nturgbd_skeletons_s001_to_s017/'
        files = os.listdir(self.path + folder)
        if not os.path.exists('./datasets'):
            os.mkdir('./datasets')
        f_cs_train = open('./datasets/cs_train.txt', 'w')
        f_cv_train = open('./datasets/cv_train.txt', 'w')
        f_cs_eval = open('./datasets/cs_eval.txt', 'w')
        f_cv_eval = open('./datasets/cv_eval.txt', 'w')

        f_ignore = open('./datasets/ignore.txt','r')
        ignore_names = f_ignore.readlines()
        ignore_names = [name.strip() for name in ignore_names]
        f_ignore.close()

        for file in files:
            file_name = file.split('.')[0]
            if file_name in ignore_names:
                continue
            cv = int(file_name[5:8])
            cs = int(file_name[9:12])

            if cv == 1:
                f_cv_eval.write(folder + file + '\n')
            else:
                f_cv_train.write(folder + file + '\n')

            if cs in [3,6,7,10,11,12,20,21,22,23,24,26,29,30,32,33,36,37,39,40]:
                f_cs_eval.write(folder + file + '\n')
            else:
                f_cs_train.write(folder + file + '\n')

        f_cs_train.close()
        f_cv_train.close()
        f_cs_eval.close()
        f_cv_eval.close()
