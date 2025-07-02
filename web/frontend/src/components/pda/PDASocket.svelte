<script lang="ts">
	import { io } from 'socket.io-client';

	const socket = io('http://localhost:5000');

	socket.on('connect', () => {
		console.log('Connected to server');
		const room = 'vibrana:hydro:x';
		socket.emit('join', { room });
		console.log(`Joined room: ${room}`);
	});

	socket.on('message', (data) => {
		console.log(data);
	});

</script>