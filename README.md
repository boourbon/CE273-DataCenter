# eec273dctcp
## Reproducing Instructions
Do step A <strong>or</strong> step B, and then do step C.
<strong> Step A </strong>
1)	Run the command below: <br>
wget http://www.kernel.org/pub/linux/kernel/v3.0/linux-3.2.18.tar.bz2 <br>
tar -xjf linux-3.2.18.tar.bz2 <br>
cd linux-3.2.18 <br>
patch -p1 </**your path to**/mininet_tests/dctcp/0001-Updated-DCTCP-patch-for-3.2-kernels.patch
make menuconfig
2)	In menuconfig, go to “Networking support”, and then go to Networking options. Enable “DCTCP: Data Center TCP”.
3)	Run the command below:
processors=1
export CONCURRENCY_LEVEL=$processors
make-kpkg clean
time fakeroot make-kpkg --verbose --initrd --append-to-version=-dctcp kernel_image kernel_headers
cd /usr/src
sudo dpkg -i linux-image-3.2.18-dctcp_3.2.18-dctcp-10.00.Custom_amd64.deb
sudo dpkg -i linux-headers-3.2.18-dctcp_3.2.18-dctcp-10.00.Custom_amd64.deb
sudo update-grub2
verify /boot/grub/grub.cfg
sudo reboot
