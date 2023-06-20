import { StyleSheet, Dimensions } from 'react-native'

export default StyleSheet.create({
    backdrop: {
        position: "absolute",
        width: Dimensions.get("screen").width,
        height: Dimensions.get("screen").height,
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
    },
    modal: {
        width: "70%",
        height: "40%",
        backgroundColor: "white",
        padding: 10,
        borderRadius: 10
    },
    invisible: { display: "none" }
})