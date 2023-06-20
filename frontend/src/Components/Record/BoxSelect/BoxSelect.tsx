import React, { useState } from 'react'
import { View, Pressable, Text, TouchableNativeFeedback, ActivityIndicator, Dimensions } from 'react-native'
import RNFetchBlob from 'rn-fetch-blob'

import VideoFirstFrame from './VideoFirstFrame'
import styles from './boxSelectStyles'
import { useAtom } from 'jotai'
import videoURI from '../../../data/video'
import response from '../../../data/videoResponse'
import LinearGradient from 'react-native-linear-gradient'

import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome'
import { faCheck } from '@fortawesome/free-solid-svg-icons/faCheck'
import { faInfo } from '@fortawesome/free-solid-svg-icons/faInfo'
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons/faArrowLeft'
import axios from 'axios'
import GestureDemo from '../Test'

function BoxSelect({ navigation, route }: any) {

    const [uri, setUri] = useAtom(videoURI)
    const [resp, setRes] = useAtom(response)

    // set loading state
    const [loading, setLoading] = useState(false)

    const [x, setx] = useState<number>(-1)
    const [y, sety] = useState<number>(-1)
    const [w, setw] = useState<number>(0)
    const [h, seth] = useState<number>(0)
    const [sub, setSub] = useState<boolean>(false)

    async function onSubmit(event: React.FormEvent<HTMLInputElement>) {
        console.log("submitting")
        setSub(true)
        event.preventDefault()
        const formdata = new FormData()
        formdata.append('file', {uri, type: "video/mp4", name: "file.mp4"})
        formdata.append('x', String(x))
        formdata.append('y', String(y))
        formdata.append('w', String(w))
        formdata.append('h', String(h))
        // RNFetchBlob.config({
        //     fileCache: true,
        //     addAndroidDownloads: {
        //         useDownloadManager: true,
        //         mime: "video/mp4",
        //         description: "video with object removed from download manager",
        //         path: `${RNFetchBlob.fs.dirs.DownloadDir}/video/vid.mp4`,
        //         notification: true
        //     }
        // })
        RNFetchBlob.fetch("POST", "https://2423-96-248-107-65.ngrok-free.app/predictions/inpaint", 
            {
                "content-type": "multipart/form-data"
            },
            [
                {name: 'data', data: RNFetchBlob.wrap(uri), filename: 'vid.mp4'},
                {name: 'x', data: String(x)},
                {name: 'y', data: String(y)},
                {name: 'w', data: String(w)},
                {name: 'h', data: String(h)},
                {name: "maxx", data: String(Dimensions.get('window').width)},
                {name: "maxy", data: String(Dimensions.get('window').height)}
            ]
        ).then(res => {
            const data = JSON.parse(res.data)
            console.log("res: ", data)
            console.log("received resbruh")

            console.log("aiwuehfiadfhkj")

            RNFetchBlob.config({
                fileCache: true,
                addAndroidDownloads: {
                    useDownloadManager: true,
                    mime: "video/mp4",
                    description: "video with object removed from download manager",
                    path: `${RNFetchBlob.fs.dirs.DownloadDir}/video/vid.mp4`,
                    notification: true
                }
            }).fetch("GET", data.url)
                .then(res => console.log("downloaded to:", res.path()))
                .catch(err => console.log("err: ", err))
        })

            // var Base64Code = res.data.split("data:video/mp4;base64,"); //base64Image is my image base64 string

            // const dirs = RNFetchBlob.fs.dirs;

            // var path = dirs.DCIMDir + "/vid.mp4";

            // RNFetchBlob.fs.writeFile(path, res.data, 'base64')
            // // .then((res: any) => {
            // //     console.log("finished...", res)
            // //     setSub(false)
            // //     navigation.navigate("Completed")
            // // }).catch(reason => {
            // //     console.log("not working!!!!!!")
            // //     console.log(reason)
            // // })
            // // console.log("finished: ", res)
            // // console.log("path: ", res.path)
            // // const dir = RNFetchBlob.fs.dirs.DocumentDir + "/vid.mp4"
            // // RNFetchBlob.fs.writeFile(dir, res.data)
            // // setSub(false)
            // // navigation.navigate("Completed")
    }

    const set = (x: number, y: number, w: number, h: number) => {
        setx(x)
        sety(y)
        setw(w)
        seth(h)
        console.log(x, " ", y, " ", w, " ", h)
    }

    return loading ? (
        <View style={styles.chooseImage}>
            <Text>LOADING</Text>
        </View>
    ) : (
        <View style={styles.chooseImage}>
            <VideoFirstFrame uri={uri} setValues={set}/>
            {/* <GestureDemo/> */}
            {/* <GestureDemo/> */}
            {/* <Text>Select an Area to Remove:</Text>
            <TextInput onChangeText={setx} value={x} placeholder="x:"/>
            <TextInput onChangeText={sety} value={y} placeholder="y:"/>
            <TextInput onChangeText={setw} value={w} placeholder="w:"/>
            <TextInput onChangeText={seth} value={h} placeholder="h:"/> */}
            <View style={styles.btnContainer}/>
                <View style={styles.actions}>
                    <View style={{borderRadius: 32.5}}>
                    <TouchableNativeFeedback background={TouchableNativeFeedback.Ripple(
                        "#00000000",
                        true
                    )} onPress={() => console.log("hola")}>
                        <View style={{width: 65, height: 65, overflow: "hidden", borderRadius: 32.5, display: "flex", justifyContent: "center", alignItems: "center"}}>
                            <FontAwesomeIcon icon={faArrowLeft} color="white" size={35}/>
                        </View>
                    </TouchableNativeFeedback>
                    </View>

                    <View style={{borderRadius: 32.5}}>
                    <TouchableNativeFeedback background={TouchableNativeFeedback.Ripple(
                        "#00000000",
                        true
                    )} onPress={() => console.log("hola")}>
                        <View style={{width: 65, height: 65, overflow: "hidden", borderRadius: 32.5, display: "flex", justifyContent: "center", alignItems: "center"}}>
                            <FontAwesomeIcon icon={faInfo} color="white" size={35}/>
                        </View>
                    </TouchableNativeFeedback>
                    </View>

                    <LinearGradient colors={['#3b82f6', '#3b82f6']}
                        style={styles.button} 
                        start={{ y: 0.0, x: 0.0 }} end={{ y: 1.0, x: 1.0 }}>
                        <Pressable onPress={onSubmit}>
                            <FontAwesomeIcon icon={faCheck} color="white" size={35}/>
                        </Pressable>
                    </LinearGradient>
                </View>
            <View style={sub ? styles.backdrop : styles.invisible}>
                <View style={sub ? styles.modal : styles.invisible}>
                    <Text>Loading...</Text>
                </View>
            </View>
            <View style={{ position: "absolute",  flex: 1, display: sub ? "flex" : "none", justifyContent: "center", alignItems: "center", width: "100%", height: "100%", backgroundColor: "#000000dd", zIndex: 500 }}>
                <ActivityIndicator size="large"/>
                <Text style={{color: "#64748b", textAlign: "center", marginTop: 25}}>{"Your inpainted video is being processed and will \nbe ready shortly"}</Text>
            </View>
        </View>

    )
}

export default BoxSelect