import React from 'react'

import {
    Button,
    NativeModules,
    SafeAreaView,
    ScrollView,
    StatusBar,
    StyleSheet,
    Text,
    TextInput,
    useColorScheme,
    View,
    Pressable,
    Image
} from 'react-native'
import LinearGradient from 'react-native-linear-gradient';
import Action from './Home/Action';


function Completed({ navigation, route }) {
    return (
        <View style={{backgroundColor: "white", height: "100%"}}>
            <LinearGradient style={styles.bottomRect} 
                colors={["#e2e8f0", "#e2e8f0"]} 
                start={{x: 0, y: 0}}
                end={{x: 1, y: 1}}/>
            <View style={styles.imgContainer}>
                <Image source={require("./video.png")} style={{ width: 300, height: 300 }}/>
            </View>
            <View style={styles.mainText}>
                <Text style={{fontSize: 36, color: "black", textAlign: "center"}}>Video <Text style={styles.highlight}>Downloaded!</Text></Text>
                <Text style={{fontSize: 17, color: "black", fontWeight:"200", textAlign: "center", width: "70%", marginLeft: "15%"}}>Go to your camera roll to view the updated video with objects removed</Text>
            </View>
            {/* <View style={styles.spacer}/> */}
            <View style={styles.actionContainer}>
                <Action title="Make a new Video" desc="Upload and alter another video" onClick={() => {console.log("test: ", navigation);navigation.navigate("Record")}}/>
            </View>
        </View>
    )
}

const styles = StyleSheet.create({
    menu: {
        position: "absolute",
        top: 25,
        left: 25,
        borderColor: "black",
        borderWidth: 2,
        zIndex: 20
    },
    topRect: {
        position: "absolute",
        width: 876.42,
        height: 173,
        left: -15,
        // backgroundColor: "#FFA89C",
        backgroundColor: "#e2e8f0",
        transform: [{ rotate: '6deg' }]
    },
    imgContainer: {
        width: "100%",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
    },
    bottomRect: {
        position: "absolute",
        width: 876.42,
        height: 273,
        left: -25,
        bottom: -15,
        // backgroundColor: "#FFA89C",
        backgroundColor: "#f1f5f9",
        transform: [{ rotate: '-6deg' }]
    },
    mainText: {
        width: "100%",
        borderColor: "black",
        letterSpacing: "0.05em",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        color: "black",
        alignContent: "center",
    },
    highlight: {
        color: "#3b82f6"
    },
    actionContainer: {
        display: "flex",
        width: "100%",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        rowGap: 5,
        position: "absolute",
        bottom: 90,
    },
    spacer: {
        height: 100
    }
})

export default Completed