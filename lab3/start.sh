qemu-system-x86_64 --enable-kvm -m 2G -net nic \
	-net user,hostfwd=tcp::2222-:22 \
	-drive file=./ubuntu18.qcow2,if=virtio \
	-drive file=seed.iso,if=virtio \
	-device edu,dma_mask=0xFFFFFFFF \
	-nographic
