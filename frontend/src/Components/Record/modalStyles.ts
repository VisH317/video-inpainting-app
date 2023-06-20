import { StyleSheet } from 'react-native'

export default StyleSheet.create({
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
        height: "50%",
        backgroundColor: "white"
    },
    invisible: { display: "none" }
})