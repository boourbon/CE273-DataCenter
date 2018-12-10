# eec273dctcp
## Reproducing Instructions
Do step A <strong>or</strong> step B, and then do step C. <br>
<strong>   Step A </strong> <br>
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
