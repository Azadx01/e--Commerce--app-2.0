import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../theme/theme';

export const Header = ({ title }: { title: string }) => (
    <View style={styles.header}>
        <Text style={styles.title}>{title}</Text>
    </View>
);

const styles = StyleSheet.create({
    header: {
        paddingTop: theme.spacing.xl,
        paddingBottom: theme.spacing.m,
        paddingHorizontal: theme.spacing.m,
        backgroundColor: theme.colors.surface,
        borderBottomWidth: 1,
        borderBottomColor: theme.colors.border,
    },
    title: {
        ...theme.typography.h1,
        color: theme.colors.text,
    }
});
