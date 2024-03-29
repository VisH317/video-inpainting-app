import { StyleSheet, Dimensions } from "react-native"  

console.log(Dimensions.get("window"))

const styles = StyleSheet.create({
    backgroundVideo: {
        zIndex: 0,
        // aspectRatio: 1,
        flex: 1,
        // alignSelf: 'stretch',
        width: Dimensions.get('window').width,
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
        justifyContent: "space-between",
        alignItems: "center",
        height: 80,
        flexDirection: "row",
        position: "absolute",
        bottom: 0,
        paddingLeft: 20,
        paddingRight: 20,
    },
    videoCont: {
        position: 'absolute',
        height: "100%",
        zIndex: 0,
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
        height: 80, 
        width: "100%", 
        position: "absolute", 
        bottom: 0, 
        left: 0,
        // zIndex:-10,
    },
    chooseImage: {
        flexDirection: 'column',
        flex: 1,
        // borderColor: "white",
        // borderWidth: 2
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