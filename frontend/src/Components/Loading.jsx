import React, { useState, useEffect } from 'react'
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
    ActivityIndicator
} from 'react-native'

function Loading(props) {
    return (
        <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
            <ActivityIndicator size="large"/>
            <Text>Your inpainted video is being processed and will be ready shortly</Text>
        </View>
    )
}

const styles = StyleSheet.create({
    view: {
        
    }
})

export default Loading