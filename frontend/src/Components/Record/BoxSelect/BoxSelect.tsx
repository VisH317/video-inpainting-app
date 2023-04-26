import React, { useState } from 'react'
import { View, Pressable, Text, TouchableNativeFeedback } from 'react-native'
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
        // "http://10.0.2.2:8080/predictions/inpaint"
        // const res = await axios.post("http://10.0.2.2:5001")
        // console.log(res)
        RNFetchBlob.fetch("POST", "https://172.17.192.1:8080/predictions/inpaint/", 
            {
                "content-type": "multipart/form-data"
            },
            [
                {name: 'data', data: RNFetchBlob.wrap(uri), filename: 'vid.mp4'},
                {name: 'x', data: String(x)},
                {name: 'y', data: String(y)},
                {name: 'w', data: String(w)},
                {name: 'h', data: String(h)},
            ]
        ).then((res: any) => {
            console.log("finished...", res)
            setSub(false)
            navigation.navigate("Completed")
        }).catch(reason => {
            console.log("not working!!!!!!")
            console.log(reason)
        })
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
            {/* <Text>Select an Area to Remove:</Text>
            <TextInput onChangeText={setx} value={x} placeholder="x:"/>
            <TextInput onChangeText={sety} value={y} placeholder="y:"/>
            <TextInput onChangeText={setw} value={w} placeholder="w:"/>
            <TextInput onChangeText={seth} value={h} placeholder="h:"/> */}
            <View style={styles.btnContainer}>
                <View style={styles.actions}>
                    <View style={{borderRadius: 32.5}}>
                    <TouchableNativeFeedback background={TouchableNativeFeedback.Ripple(
                        "#00000000",
                        true
                    )} onPress={() => console.log("hola")}>
                        <View style={{width: 65, height: 65, overflow: "hidden", borderRadius: 32.5, display: "flex", justifyContent: "center", alignItems: "center"}}>
                            <FontAwesomeIcon icon={faArrowLeft} color="#333" size={35}/>
                        </View>
                    </TouchableNativeFeedback>
                    </View>

                    <View style={{borderRadius: 32.5}}>
                    <TouchableNativeFeedback background={TouchableNativeFeedback.Ripple(
                        "#00000000",
                        true
                    )} onPress={() => console.log("hola")}>
                        <View style={{width: 65, height: 65, overflow: "hidden", borderRadius: 32.5, display: "flex", justifyContent: "center", alignItems: "center"}}>
                            <FontAwesomeIcon icon={faInfo} color="#333" size={35}/>
                        </View>
                    </TouchableNativeFeedback>
                    </View>

                    <LinearGradient colors={['#FF8C67', '#FFA89C']}
                        style={styles.button} 
                        start={{ y: 0.0, x: 0.0 }} end={{ y: 1.0, x: 1.0 }}>
                        <Pressable onPress={onSubmit}>
                            <FontAwesomeIcon icon={faCheck} color="#333" size={35}/>
                        </Pressable>
                    </LinearGradient>
                </View>
            </View>
            <View style={sub ? styles.backdrop : styles.invisible}>
                <View style={sub ? styles.modal : styles.invisible}>
                    <Text>Loading...</Text>
                </View>
            </View>
        </View>

    )
}

export default BoxSelect