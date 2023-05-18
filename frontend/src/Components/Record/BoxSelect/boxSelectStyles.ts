import { StyleSheet } from "react-native"  

const styles = StyleSheet.create({
    backgroundVideo: {
        zIndex: 0,
        aspectRatio: 1,
        flex: 1,
        width: "95%",
        borderWidth: 2,
        borderColor: 'black',
    },
    button: {
        zIndex: 3,
        backgroundColor: "#FF8C67",
        width: 65,
        textAlign: 'center',
        alignItems: "center",
        justifyContent: "center",
        height: 65,
        borderRadius: 32.5
    },
    actions: {
        zIndex: 300,
        width: "100%",
        display: "flex",
        justifyContent: "space-around",
        alignItems: "center",
        height: 80,
        flexDirection: "row",
    },
    videoCont: {
        position: 'absolute',
        height: 635,
        zIndex: 0,
        width: "100%",
        alignItems: 'center',
        borderColor: 'black',
        flex: 1,
        display: "flex",
        // borderWidth: 2

    },
    btnContainer: {
        flex: 1, 
        flexDirection: "column-reverse", 
        height: 635, 
        width: "100%", 
        position: "absolute", 
        top: 0, 
        left: 0,
        zIndex:-10,
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