"""
main_ndt_slam_server.py
File for the offline implementation of NDT-SLAM on the Talbot 330 resident powerhouse machine
Author: Ashwin Kanhere
Date Created: 16th June 2019
Date Modified: 16th June, 2019
"""
import numpy as np
import pptk
import ndt
import odometry
import diagnostics
import time
import utils
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


folder_location = '/home/kanhere2/ion-gnss-19/uiuc_dataset/'
filename = 'pc_'
ext = '.csv'

icp_odom = np.load('saved_icp_odom.npy')
icp_odom = -icp_odom
ndt_odom = np.load('saved_ndt_odom.npy')
diff_ndt = np.zeros_like(ndt_odom)
diff_icp = np.zeros_like(icp_odom)
cand_transform = np.array([0.3, 0.3, 0.001, 0.25, 0.25, 0.5])
for i in range(icp_odom.shape[0]):
    diff_ndt[i, :] = -ndt_odom[i, :] - cand_transform
    diff_icp[i, :] = icp_odom[i, :] - cand_transform
print(np.mean(np.abs(diff_ndt), axis=0))
print(np.mean(np.abs(diff_icp), axis=0))
"""
test = np.loadtxt(folder_location+filename+str(676)+ext, delimiter=',')
test2 = np.loadtxt(folder_location+filename+str(675)+ext, delimiter=',')
pptk.viewer(test)
pptk.viewer(test2)
test_cloud = ndt.ndt_approx(test)
ndt.display_ndt_cloud(test_cloud)
test_cloud2 = ndt.ndt_approx(test2)
ndt.display_ndt_cloud(test_cloud2)
result_odom = odometry.odometry(test_cloud2, test)
update_points = test_cloud2.points_in_filled_voxels(test)
pptk.viewer(update_points)
ndt.display_ndt_cloud(test_cloud2)
result_pc = utils.transform_pc(utils.invert_odom_transfer(result_odom), update_points)
test_cloud2 = ndt.ndt_approx(test2)
print(test_cloud2.find_integrity(result_pc))
print(test_cloud2.find_integrity(test))
"""
"""
first_idx = 500
last_idx = 675
num_run = last_idx - first_idx
ndt_odom = np.zeros([num_run, 6])
icp_odom = np.zeros([num_run, 6])
cand_transform = np.array([0.3, 0.3, 0.001, 0.25, 0.25, 0.5])
for idx in range(first_idx, last_idx):
    t0 = time.time()
    print('Loading point cloud number: ', idx)
    curr_pc = np.loadtxt(folder_location+filename+str(idx)+ext, delimiter=',')
    trans_pc = utils.transform_pc(cand_transform, curr_pc)
    trans_ndt = ndt.ndt_approx(trans_pc)
    print('Calculating odometry:', idx)
    curr_ndt_odom_inv = odometry.odometry(trans_ndt, curr_pc)
    curr_icp_odom = diagnostics.ind_lidar_odom(curr_pc, trans_pc)
    print('NDT ODOMETRY: ', curr_ndt_odom_inv)
    print('ICP ODOMETRY: ', curr_icp_odom)
    ndt_odom[idx - first_idx, :] = utils.invert_odom_transfer(curr_ndt_odom_inv)
    icp_odom[idx - first_idx, :] = curr_icp_odom
    print('PC: ', idx, 'Run Time: ', time.time() - t0)
np.save('saved_ndt_odom', ndt_odom)
np.save('saved_icp_odom', icp_odom)
"""
"""
for idx in range(first_idx, last_idx):
    t0 = time.time()
    print('Loading point cloud number: ', idx)
    curr_pc = np.loadtxt(folder_location+filename+str(idx)+ext, delimiter=',')
    prev_ndt = ndt.ndt_approx(prev_pc)
    print('Calculating odometry:', idx)
    curr_ndt_odom_inv = odometry.odometry(prev_ndt, curr_pc)
    N1 = prev_pc.shape[0]
    N2 = curr_pc.shape[0]
    if N1 <= N2:
        curr_icp_odom = diagnostics.ind_lidar_odom(curr_pc[:N1, :], prev_pc)
    else:
        curr_icp_odom = diagnostics.ind_lidar_odom(curr_pc, prev_pc[:N2, :])
    ndt_odom[idx - first_idx, :] = utils.invert_odom_transfer(curr_ndt_odom_inv)
    icp_odom[idx - first_idx, :] = curr_icp_odom
    state = utils.combine_odometry(state, ndt_odom[idx - first_idx, :])
    update_points = prev_ndt.points_in_filled_voxels(curr_pc)
    trans_update_points = utils.transform_pc(state, update_points)
    map_ndt.update_cloud(trans_update_points)
    prev_pc = curr_pc
    print('PC: ', idx, 'Run Time: ', time.time() - t0)
np.save('saved_ndt_odom', ndt_odom)
np.save('saved_icp_odom', icp_odom)
ndt.display_ndt_cloud(map_ndt)
"""
"""
ndt_odom = np.load('saved_ndt_odom_4.npy')
icp_odom = np.load('saved_icp_odom_4.npy')
N = ndt_odom.shape[0]
total_ndt_odom = np.zeros_like(ndt_odom)
total_icp_odom = np.zeros_like(icp_odom)
for i in range(1, N):
    total_ndt_odom[i, :] = utils.combine_odometry(total_ndt_odom[i-1, :], ndt_odom[i, :])
    total_icp_odom[i, :] = utils.combine_odometry(total_icp_odom[i-1, :], icp_odom[i, :])
print(np.mean(np.abs(total_ndt_odom - total_icp_odom)))
print(np.mean(np.abs(ndt_odom - icp_odom)))
plt.interactive(False)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(total_ndt_odom[:, 0], total_ndt_odom[:, 1], total_ndt_odom[:, 2], s=4)
#ax.scatter(total_icp_odom[:, 0], total_icp_odom[:, 1], total_icp_odom[:, 2], s=4)
plt.show()
"""



