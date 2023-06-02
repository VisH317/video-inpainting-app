import React, { useEffect, useRef, useState } from 'react'
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler'
import { View, Text, Dimensions } from 'react-native'
import Video from 'react-native-video'

import styles from './boxSelectStyles'

interface VideoFrameProps {
    setValues: (x: number, y: number, w: number, h: number) => void
    uri: string
}

export default function VideoFirstFrame(props: VideoFrameProps) {
    const [p, setp] = useState(false)

    // gestures
    const [x, setx] = useState(-10)
    const [y, sety] = useState(-10)
    const [w, setw] = useState(0)
    const [h, seth] = useState(0)

    // states for bounding box
    const [absx, setabsx] = useState(-10)
    const [absy, setabsy] = useState(-10)
    const [absxf, setabsxf] = useState(0)
    const [absyf, setabsyf] = useState(0)

    const pan = Gesture.Pan()
        .onStart((g) => {
            setx(Math.round(g.x)) 
            sety(Math.round(g.y))
            setabsx(Math.round(g.absoluteX))
            setabsy(Math.round(g.absoluteY))
        })
        .onUpdate(g => {
            setabsxf(Math.round(g.absoluteX))
            setabsyf(Math.round(g.absoluteY))
        })
        .onEnd((g) => {
            setw(Math.abs(Math.round(g.x)-x))
            seth(Math.abs(Math.round(g.y)-y))
            setabsxf(Math.round(g.absoluteX))
            setabsyf(Math.round(g.absoluteY))
            console.log("alewsjfoiawj")
            props.setValues(x, y, Math.abs(Math.round(g.x)-x), Math.abs(Math.round(g.y)-y))
            player?.measure((a: number, b: number, c: number, d: number, e: number, f: number) => console.log("helloooo"))
        })

    const boundingBoxStyle = {
        borderColor: "#2563eb",
        borderWidth: 2,
        position: "absolute",
        top: absy,
        left: absx,
        width: absxf-absx,
        height: absyf-absy,
        zIndex: 100
    }

    let player: any

    return (
        <GestureHandlerRootView style={{flex:1,zIndex:0}}>
            <View style={styles.videoCont}>
                <View style={boundingBoxStyle}/>
                <GestureDetector gesture={pan} style={styles.videoCont}>
                    <Video source={{uri: props.uri}} ref={ref=>player=ref} controls={false} paused={p}
                        onBuffer={() => console.log("buffering")} onError={() => console.log("ERROR")}
                        style={styles.backgroundVideo} onLoad={() => {
                            // player.seek(5)
                            // setp(true)
                            console.log(Object.getOwnPropertyNames(player.state))
                            player.seek(0)
                    }} onEnd={() => {setp(true);player.seek(0)}} posterResizeMode='cover' resizeMode="stretch"/>
                    {/* <View style={{ flex: 1, backgroundColor: "black" }}>
                    <Text
                        style={{ color: "white", fontSize: 24 }}
                    >{`Gesture started at:  ${x}`}</Text>
                    <Text
                        style={{ color: "white", fontSize: 24 }}
                    >{`Gesture moved to:  ${y}`}</Text>
                    <Text
                        style={{ color: "white", fontSize: 24 }}
                    >{`Gesture updated to:  ${w}`}</Text>
                    <Text
                        style={{ color: "white", fontSize: 24 }}
                    >{`Gesture ended at:  ${h}`}</Text>
                    </View> */}
                </GestureDetector>
            </View>
        </GestureHandlerRootView>
    )
}