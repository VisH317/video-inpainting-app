import { StyleSheet, Dimensions } from "react-native"  

console.log(Dimensions.get("window"))

const styles = StyleSheet.create({
    backgroundVideo: {
        // zIndex: 100,
        // aspectRatio: 1,
        flex: 1,
        // alignSelf: 'stretch',
        width: Dimensions.get('window').width,
        borderWidth: 2,
        borderColor: 'blue',
        // alignSelf: 'center',
        height: Dimensions.get('window').height,
        // resizeMode: "cover"
    },
    button: {
        // zIndex: 3,
        backgroundColor: "#FF8C67",
        width: 65,
        textAlign: 'center',
        alignItems: "center",
        justifyContent: "center",
        height: 65,
        borderRadius: 32.5,
    },
    actions: {
        zIndex: 20,
        width: "100%",
        display: "flex",
        justifyContent: "space-around",
        alignItems: "center",
        height: 80,
        flexDirection: "row",
        // borderWidth: 2,
        // borderColor: "red",
        position: "absolute",
        bottom: 0,
    },
    videoCont: {
        position: 'absolute',
        height: "100%",
        // zIndex: 90,
        width: "100%",
        alignItems: 'center',
        // borderColor: 'black',
        flex: 1,
        display: "flex",
        // borderWidth: 2

    },
    btnContainer: {
        flex: 1, 
        flexDirection: "column-reverse", 
        height: 100, 
        width: "100%", 
        position: "absolute", 
        bottom: 0, 
        left: 0,
        // zIndex:-10,
        borderWidth: 2,
        borderColor: "black",
    },
    chooseImage: {
        flexDirection: 'column',
        flex: 1
    },
    text: {
        fontSize: 30
    },
    invisible: { display: "none" },
    backdrop: {
        position: "absolute",
        width: "100%",
        height: "100%",
        backgroundColor: "rgba(0, 0, 0, 0.3)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
    },
    modal: {
        width: "50%",
        height: "50%"
    }
})

export default styles