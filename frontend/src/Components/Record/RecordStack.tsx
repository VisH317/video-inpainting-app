import React from 'react'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import Record from './Record'
import BoxSelect from './BoxSelect/BoxSelect'
import Completed from '../Completed'
import { SafeAreaView } from 'react-native-safe-area-context'
import { StyleSheet } from 'react-native'
import { faBars } from '@fortawesome/free-solid-svg-icons'
import { View } from 'react-native'
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome'

const Stack = createNativeStackNavigator()

export default function RecordStack({ navigation }) {
    return (
        <SafeAreaView>
            <View style={styles.menu}>
                <FontAwesomeIcon icon={faBars} size={30} color="#3b82f6"/>
            </View>
            <Stack.Navigator screenOptions={{headerShown: false}}>
                <Stack.Screen name="Record" component={Record}/>
                <Stack.Screen name="Select" component={BoxSelect}/>
                <Stack.Screen name="Completed" component={Completed}/>
            </Stack.Navigator>
        </SafeAreaView>
    )
}

const styles = StyleSheet.create({
    menu: {
        position: "absolute",
        top: 25,
        left: 25
    }
})