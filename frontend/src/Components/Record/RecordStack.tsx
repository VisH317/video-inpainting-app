import React from 'react'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import Record from './Record'
import BoxSelect from './BoxSelect/BoxSelect'
import Completed from '../Completed'

const Stack = createNativeStackNavigator()

export default function RecordStack() {
    return (
        <Stack.Navigator screenOptions={{headerShown: false}}>
            <Stack.Screen name="Record" component={Record}/>
            <Stack.Screen name="Select" component={BoxSelect}/>
            <Stack.Screen name="Completed" component={Completed}/>
        </Stack.Navigator>
    )
}