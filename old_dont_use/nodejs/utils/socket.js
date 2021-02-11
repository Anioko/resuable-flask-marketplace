'use strict';

const moment = require('moment');
const path = require('path');
const fs = require('fs');
const helper = require('./helper');

class Socket{

    constructor(socket){
        this.io = socket;
    }

    socketEvents(){
        this.io.on('connection', (socket) => {
            socket.on('connected', async () => {
                let user = await helper.getUser(socket.id);
                let sockets = [];
                if (helper.IsJsonString(user.socket_id)){
                    sockets = JSON.parse(user.socket_id);
                    if (typeof(sockets) === 'string' || sockets === null){
                        sockets = [];
                    }
                }
                let connected = [];
                for (let i=0; i < sockets.length; i++){
                    if(this.io.sockets.sockets[sockets[i]]!=undefined){
                        connected.push(sockets[i]);
                    }
                }
                const response = await helper.updateSockets( user.id, connected);
                if (user){
                    // console.log("user_connected " + user.first_name+ " " + user.last_name);
                    socket.broadcast.emit('user_connected', {
                        user_id: user.id,
                        socket_id: user.socket_id
                    });
                }
            });
            socket.on('reconnect',  (data) => {
                // console.log(data);
                // let user = await helper.getUser(socket.id);
                // console.log(user.first_name);
                // console.log(reason);
            });
            socket.on('refresh',  (data) => {
                // console.log(data);
                // let user = await helper.getUser(socket.id);
                // console.log(user.first_name);
                // console.log(reason);
            });
            socket.on('reconnect_attempt',  (data) => {
                // console.log(data);
                // let user = await helper.getUser(socket.id);
                // console.log(user.first_name);
                // console.log(reason);
            });

            /**
             * get the get messages
             */
            socket.on('getMessages', async (data) => {
                const result = await helper.getMessages(data.fromUserId, data.toUserId);
                if (result === null) {
                    this.io.to(socket.id).emit('getMessagesResponse', {result:[],toUserId:data.toUserId});
                }else{
                    this.io.to(socket.id).emit('getMessagesResponse', {result:result,toUserId:data.toUserId});
                }
            });
            socket.on('message_sent', async function(data){
                let sender = await helper.getUser(socket.id);
                let user = await helper.getUserById(data.message.recipient_id);
                let sockets = [];
                if (helper.IsJsonString(user.socket_id)){
                    sockets = JSON.parse(user.socket_id);
                    if (typeof(sockets) === 'string' || sockets === null){
                        sockets = [];
                    }
                }
                for (let i=0; i < sockets.length; i++){
                        socket.to(sockets[i]).emit('message_received', {message: data.message});
                }
                                let sender_sockets = [];
                if (helper.IsJsonString(sender.socket_id)){
                    sender_sockets = JSON.parse(sender.socket_id);
                    if (typeof(sender_sockets) === 'string' || sender_sockets === null){
                        sender_sockets = [];
                    }
                }
                sender_sockets = sender_sockets.filter((value, index, arr)=> {return value != socket.id;});
                for (let i=0; i < sender_sockets.length; i++){
                        socket.to(sender_sockets[i]).emit('new_message_sent', {message: data.message});
                }

            });
            socket.on("new_notification", function (data) {
                let sockets = [];
                if (helper.IsJsonString(data.notification.touser.socket_id)){
                    sockets = JSON.parse(data.notification.touser.socket_id);
                    if (typeof(sockets) === 'string' || sockets === null){
                        sockets = [];
                    }
                }
                for (let i=0; i < sockets.length; i++){
                        socket.to(sockets[i]).emit('new_notification', {notification: data.notification});
                }
            });
            /**
             * send the messages to the user
             */
            socket.on('addMessage', async (response) => {
                response.date = new moment().format("Y-MM-D");
                response.time = new moment().format("hh:mm A");
                this.insertMessage(response, socket);
                socket.to(response.toSocketId).emit('addMessageResponse', response);
            });

            socket.on('typing', function (data) {
                socket.to(data.socket_id).emit('typing', {typing:data.typing, to_socket_id:socket.id});
            });

            socket.on('upload-image', async (response) => {
                let dir = moment().format("D-M-Y")+ "/" + moment().format('x') + "/" + response.fromUserId
                await helper.mkdirSyncRecursive(dir);
                let filepath = dir + "/" + response.fileName;
                var writer = fs.createWriteStream(path.basename('uploads') + "/" + filepath, { encoding: 'base64'});
                writer.write(response.message);
                writer.end();
                writer.on('finish', function () {
                    response.message = response.fileName;
                    response.filePath = filepath;
                    response.date = new moment().format("Y-MM-D");
                    response.time = new moment().format("hh:mm A");
                    this.insertMessage(response, socket);
                    socket.to(response.toSocketId).emit('addMessageResponse', response);
                    socket.emit('image-uploaded', response);
                }.bind(this));
            });

            socket.on('disconnect', async () => {
                let user = await helper.getUser(socket.id);
                const isLoggedOut = await helper.logoutUser(socket.id);
                if (user){
                    // console.log("user_disconnected " + user.first_name+ " " + user.last_name);
                    socket.broadcast.emit('user_disconnected', {
                        user_id: user.id,
                        socket_id: user.socket_id
                    });
                }
            });
            socket.on('error', (error) => {
                console.log(error);
            });
        });
    }

    async insertMessage(data, socket){
        const sqlResult = await helper.insertMessages({
            type: data.type,
            fileFormat: data.fileFormat,
            filePath: data.filePath,
            fromUserId: data.fromUserId,
            toUserId: data.toUserId,
            message: data.message,
            date: data.date,
            time: data.time,
            ip: socket.request.connection.remoteAddress
        });
    }

    socketConfig(){
        // this.io.use();

        this.io.use( async (socket, next) => {
            let userId = socket.request._query['token'];
            let userSocketId = socket.id;
            const response = await helper.addSocketId( userId, userSocketId);
            if(response &&  response !== null){
                next();
            }else{
                console.error(`Socket connection failed, for  user Id ${userId}.`);
            }
        });
        this.socketEvents();
    }
}
module.exports = Socket;
