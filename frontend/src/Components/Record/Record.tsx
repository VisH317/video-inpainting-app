import React, { useState, useEffect, useRef } from 'react'
import { StyleSheet, Text, SafeAreaView, View, Pressable, Dimensions } from 'react-native'
import videoURI from '../../data/video'
import { useAtom } from 'jotai'
import modalStyles from './modalStyles'

import { Switch, GestureHandlerRootView } from 'react-native-gesture-handler'

import { useCameraDevices, Camera } from 'react-native-vision-camera'
import { launchImageLibrary } from 'react-native-image-picker'

import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome'
import { faFileUpload } from '@fortawesome/free-solid-svg-icons/faFileUpload'
import { faInfo } from '@fortawesome/free-solid-svg-icons/faInfo'
import Modal from './Modal'

async function getVideos() {
    const params = {
        mediaType: "video" as const
    }
    const videos = await launchImageLibrary(params)
    return videos.assets
}

export default function Record({ navigation }: any) {
    const devices = useCameraDevices('telephoto-camera')
    const device = devices.back
    // console.log("devices: ", device)

    const [isRecording, setRec] = useState(false)
    const camera = useRef<Camera>(null)
    const [uri, setUri] = useAtom(videoURI)

    const updateVideos = async () => {
        const video = await getVideos()
        if(video===undefined) return
        setUri(video[0].uri)
        console.log(video[0].uri)
        navigation.navigate("Select")
    }

    const [cameraPerm, setCameraPerm] = useState(false)

// Checks Mic and Video Permissions as soon as page loads
    useEffect(() => {
    checkPermissions();
    }, []);


    // Called in a useEffect to gain permissions
    const checkPermissions = async () => {
        // Request Permissions on component load
        await Camera.requestCameraPermission();
        await Camera.requestMicrophonePermission();
        // await requestPermission()

        const cameraPermission = await Camera.getCameraPermissionStatus();
        // setCameraPerm(cameraPermission)
        const microphonePermission = await Camera.getMicrophonePermissionStatus();
    };


    const startRecording = async () => {
        if(!isRecording) {
            if(camera.current===null) return
            await camera.current.startRecording({
                flash: 'auto',
                onRecordingFinished: vid => {
                    setUri(vid.path)
                    console.log(uri)
                    navigation.navigate("Select")
                },
                onRecordingError: err => console.log(err)
            })
            setRec(true)
        } else {
            if(camera.current===null) return
            await camera.current.stopRecording()
            setRec(false)
        }
    }

    // modal states
    const [info, setInfo] = useState<boolean>(false)
    const [settings, setSettings] = useState<boolean>(false)

    // settings states
    const [setting1, setSetting1] = useState<boolean>(false)
    const toggle = (value: any) => {
        console.log("hello")
        setSetting1(prevState => !prevState)
    }

    const [switchValue, setSwitchValue] = useState(false);

    const toggleSwitch = (value) => {
        //onValueChange of the switch this function will be called
        setSwitchValue(value);
        //state changes according to switch
        //which will result in re-render the text
    };


    if(device==null) return <View style={modalStyles.backdrop}><View style={{display: "flex", justifyContent: "center", alignItems: "center"}}><Text>LOADING</Text></View></View>
    return (
        <GestureHandlerRootView>
            <Camera style={styles.camera} device={device} video={true} ref={camera} isActive/>
            <View style={{flex: 1, flexDirection: "column-reverse", width: "100%", position: "absolute", top: 0, left: 0, height: Dimensions.get("screen").height-70, zIndex: 0}}>
                <View style={styles.btnContainer}>
                    <Pressable style={styles.upload} onPressOut={updateVideos}>
                        <Text><FontAwesomeIcon icon={faFileUpload} color="white" size={25}/></Text>
                    </Pressable>
                    <Pressable style={isRecording ? styles.startActive : styles.start} onPressOut={startRecording}><Text></Text></Pressable>
                    <Pressable onPress={() => setInfo(true)}><FontAwesomeIcon icon={faInfo} color="white" size={25}/></Pressable>
                </View>
            </View>
            <Modal open={info} close={() => setInfo(false)}>
                <View style={infoStyles.container}>
                    <Text style={infoStyles.header}>Video<Text style={{color: "#3b82f6"}}>Paint</Text></Text>
                    <View style={infoStyles.spacer}/>
                    <Text style={infoStyles.content}>Instantly edit your videos and remove objects using AI. Record or upload a video and select an object to be removed</Text>
                    <HR/>
                    <Text style={{fontWeight: "600", fontSize: 17, color: "#1e293b"}}>Settings</Text>
                    <View style={infoStyles.spacer}/>
                    <View style={infoStyles.setting}>
                        {/* <Text>Setting #1</Text>
                        <Switch
                            trackColor={{false: '#94a3b8', true: '#94a3b8'}}
                            thumbColor={setting1 ? '#3b82f6' : '#f4f3f4'}
                            onValueChange={toggle}
                            value={setting1}
                            style={{zIndex: 10000}}
                        /> */}
                    </View>
                </View> 
            </Modal>
        </GestureHandlerRootView>
    )
}


const HR = () => (
    <>
        <View style={{height: 10}}/>
        <View style={{borderBottomWidth: 2, borderBottomColor: "#94a3b8", width: "60%"}}/>
        <View style={{height: 10}}/>
    </>
)


const infoStyles = StyleSheet.create({
    container: {
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        flexDirection: "column",
        paddingTop: 10,
        paddingBottom: 5,
        // borderWidth: 5,
        borderColor: "black",
        zIndex: 20
    },
    header: {
        fontWeight: "700", 
        color: "#1e293b", 
        fontSize: 30,
        // borderWidth: 5,
        borderColor: "black"
    },
    spacer: { height: 10 },
    content: {
        fontWeight: "300",
        color: "#64748b",
        fontSize: 14,
        textAlign: "center",
        // borderWidth: 5,
        borderColor: "black"
    },
    setting: {
        width: "80%",
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
        // borderWidth: 5,
        borderColor: "black",
        zIndex: 1000
    },
})

const styles = StyleSheet.create({
    camera: {
        height: 685,
        flex: 1,
        width: "100%",
        position: "absolute",
        top: 0,
        left: 0,
        // borderColor: "black",
        // borderWidth: 50,
        color: "white"
    },
    btnContainer: {
        width: "100%",
        borderColor: "black",
        // borderWidth: 5,
        zIndex: 100,
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-around",
        padding: 5,
        alignItems: "center",
        // position: "absolute",
        // bottom: 0,
        // left: 0,
        // height: 100
    },
    start: {
        width: 60,
        height: 60,
        backgroundColor: "transparent",
        borderRadius: 30,
        borderColor: "white",
        borderWidth: 5,
    },
    startActive: {
        width: 60,
        height: 60,
        backgroundColor: "#3b82f6",
        padding: 2,
        borderRadius: 30,
        borderColor: "#3b82f6",
        borderWidth: 5,
    },
    upload: {
        width: 20,
        height: 20,
        backgroundColor: "transparent",
        color: "white",
        // left: "calc(25%-10px)",
        // top: "85%"
    }
})