# eec273dctcp
## Reproducing Instructions
Do step A <strong>or</strong> step B, and then do step C. <br>
<strong>Step A</strong> <br>
1)	Run the command below: <br>
wget http://www.kernel.org/pub/linux/kernel/v3.0/linux-3.2.18.tar.bz2 <br>
tar -xjf linux-3.2.18.tar.bz2 <br>
cd linux-3.2.18 <br>
patch -p1 </**your path to**/mininet_tests/dctcp/0001-Updated-DCTCP-patch-for-3.2-kernels.patch <br>
make menuconfig <br>
2)	In menuconfig, go to "Networking support", and then go to "Networking options". Enable "DCTCP: Data Center TCP". <br>
3)	Run the command below:<br>
processors=1 <br>
export CONCURRENCY_LEVEL=$processors <br>
make-kpkg clean <br>
time fakeroot make-kpkg --verbose --initrd --append-to-version=-dctcp kernel_image kernel_headers <br>
cd /usr/src <br>
sudo dpkg -i linux-image-3.2.18-dctcp_3.2.18-dctcp-10.00.Custom_amd64.deb <br>
sudo dpkg -i linux-headers-3.2.18-dctcp_3.2.18-dctcp-10.00.Custom_amd64.deb <br>
sudo update-grub2 <br>
verify /boot/grub/grub.cfg <br>
sudo reboot <br>
<strong>Step B</strong> <br>
1)	Login to AWS. In “Services”, choose “EC2” and select the region “US West (Oregon)”. Then click “Launch Instance”. <br>
2)	In “Choose AMI”, type “DCTCP” into the search window and you will get some search results in Community AMIs, which are free to use DCTCP enabled Linux kernels. Select one and get into the next step. <br>
3)	In “Choose Instance Type”, select a medium or larger instance. The free tier eligible micro instance is not good for this experiment because it’s a shared tenancy, and the experimental data can be very unstable. However, you can try your setup and verify the correctness of your code using the micro one.  <br>
4)	In “Configure Instance” -> “Tenancy”, select “Detected”. Then in “Configure Security Group”, set your security group. Then click “Review and Launch” -> “Launch”. Before successfully launching, you need to create a key pair, which is a .pem file. Then your kernel will be launched and ready for use. <br>
5)	Connect your instance with an SSH client using the IPv4 Public IP or Public DNS of the instance and the created key. The default username is “Ubuntu”. <br>
<strong>Step C</strong>
1)	Pull the code from our repository using the command below: <br>
git clone https://github.com/boourbon/eec273dctcp.git <br>
2)	Run the experiment using the command below: <br>
         sudo chmod -R 777 eec273dctcp  # Expand permissions <br>
         cd eec273dctcp <br>
         sudo ./run.sh  #Run the experiment <br>
The code will run for about 45 minutes, and when it finishes running, the three graphs will be plotted and saved in “./eec273dctcp/graphs”. <br>

